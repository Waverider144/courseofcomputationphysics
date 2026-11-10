// Periodic vacuum Yee, six SoA fields, plus a component-layout microbenchmark.
#include <cuda_runtime.h>
#include <algorithm>
#include <cmath>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <vector>

#define CUDA(call) do { cudaError_t e=(call); if(e!=cudaSuccess){ \
  std::fprintf(stderr,"%s\n",cudaGetErrorString(e)); return 2; } } while(0)

__global__ void magnetic(double* f,int n,double s){
  int i=blockIdx.x*blockDim.x+threadIdx.x, v=n*n*n;
  if(i>=v) return;
  int x=i/(n*n),y=(i/n)%n,z=i%n;
  int xp=((x+1)%n)*n*n+y*n+z,yp=x*n*n+((y+1)%n)*n+z,zp=x*n*n+y*n+(z+1)%n;
  f[3*v+i]-=s*((f[2*v+yp]-f[2*v+i])-(f[v+zp]-f[v+i]));
  f[4*v+i]-=s*((f[zp]-f[i])-(f[2*v+xp]-f[2*v+i]));
  f[5*v+i]-=s*((f[v+xp]-f[v+i])-(f[yp]-f[i]));
}
__global__ void electric(double* f,int n,double s){
  int i=blockIdx.x*blockDim.x+threadIdx.x,v=n*n*n;
  if(i>=v) return;
  int x=i/(n*n),y=(i/n)%n,z=i%n;
  int xm=((x+n-1)%n)*n*n+y*n+z,ym=x*n*n+((y+n-1)%n)*n+z,zm=x*n*n+y*n+(z+n-1)%n;
  f[i]+=s*((f[5*v+i]-f[5*v+ym])-(f[4*v+i]-f[4*v+zm]));
  f[v+i]+=s*((f[3*v+i]-f[3*v+zm])-(f[5*v+i]-f[5*v+xm]));
  f[2*v+i]+=s*((f[4*v+i]-f[4*v+xm])-(f[3*v+i]-f[3*v+ym]));
}
__global__ void component_copy(const double* in,double* out,int v,int stride){
  int i=blockIdx.x*blockDim.x+threadIdx.x;
  if(i<v) out[i]=in[stride*i];
}
void cpu_step(std::vector<double>& f,int n,double s){
  int v=n*n*n;
  for(int i=0;i<v;i++){
    int x=i/(n*n),y=(i/n)%n,z=i%n;
    int xp=((x+1)%n)*n*n+y*n+z,yp=x*n*n+((y+1)%n)*n+z,zp=x*n*n+y*n+(z+1)%n;
    f[3*v+i]-=s*((f[2*v+yp]-f[2*v+i])-(f[v+zp]-f[v+i]));
    f[4*v+i]-=s*((f[zp]-f[i])-(f[2*v+xp]-f[2*v+i]));
    f[5*v+i]-=s*((f[v+xp]-f[v+i])-(f[yp]-f[i]));
  }
  for(int i=0;i<v;i++){
    int x=i/(n*n),y=(i/n)%n,z=i%n;
    int xm=((x+n-1)%n)*n*n+y*n+z,ym=x*n*n+((y+n-1)%n)*n+z,zm=x*n*n+y*n+(z+n-1)%n;
    f[i]+=s*((f[5*v+i]-f[5*v+ym])-(f[4*v+i]-f[4*v+zm]));
    f[v+i]+=s*((f[3*v+i]-f[3*v+zm])-(f[5*v+i]-f[5*v+xm]));
    f[2*v+i]+=s*((f[4*v+i]-f[4*v+xm])-(f[3*v+i]-f[3*v+ym]));
  }
}
int main(int argc,char**argv){
  int devices=0; cudaError_t status=cudaGetDeviceCount(&devices);
  if(status!=cudaSuccess || devices==0){
    std::printf("{\"status\":\"unavailable\",\"reason\":\"%s\",\"device_count\":%d}\n",
                cudaGetErrorString(status),devices);
    return 77;
  }
  int n=argc>1?std::atoi(argv[1]):32;
  if(n<4||n>256) return 1;
  int v=n*n*n,steps=30,threads=128,blocks=(v+threads-1)/threads;
  double h=1./n,dt=.4*h,pi=std::acos(-1.);
  std::vector<double> initial(6*v,0.),reference;
  for(int i=0;i<v;i++){
    int x=i/(n*n);
    initial[v+i]=std::sin(2*pi*x*h);
    initial[5*v+i]=std::sin(2*pi*(x*h+.5*h+.5*dt));
  }
  reference=initial;
  for(int t=0;t<steps;t++) cpu_step(reference,n,dt/h);
  double *device,*out,*aos;
  CUDA(cudaMalloc(&device,6*v*sizeof(double)));
  CUDA(cudaMalloc(&aos,6*v*sizeof(double)));
  CUDA(cudaMalloc(&out,v*sizeof(double)));
  std::vector<double> probe(6*v),probe_reference;
  for(int i=0;i<6*v;i++) probe[i]=.01*std::sin(.17*(i+1));
  probe_reference=probe;
  for(int t=0;t<3;t++) cpu_step(probe_reference,n,dt/h);
  CUDA(cudaMemcpy(device,probe.data(),6*v*sizeof(double),cudaMemcpyHostToDevice));
  for(int t=0;t<3;t++){
    magnetic<<<blocks,threads>>>(device,n,dt/h);
    electric<<<blocks,threads>>>(device,n,dt/h);
  }
  CUDA(cudaDeviceSynchronize());
  CUDA(cudaMemcpy(probe.data(),device,6*v*sizeof(double),cudaMemcpyDeviceToHost));
  double general_error=0;
  for(int i=0;i<6*v;i++) general_error=std::max(general_error,std::abs(probe[i]-probe_reference[i]));
  if(general_error>1e-10){
    std::fprintf(stderr,"general_field_cpu_difference=%.17g\n",general_error);
    for(int i=0;i<6*v;i++) if(std::abs(probe[i]-probe_reference[i])>.5*general_error){
      std::fprintf(stderr,"index=%d device=%.17g cpu=%.17g\n",i,probe[i],probe_reference[i]);
      break;
    }
    return 4;
  }
  CUDA(cudaMemcpy(device,initial.data(),6*v*sizeof(double),cudaMemcpyHostToDevice));
  magnetic<<<blocks,threads>>>(device,n,dt/h);
  electric<<<blocks,threads>>>(device,n,dt/h);
  CUDA(cudaDeviceSynchronize());
  auto wall_start=std::chrono::steady_clock::now();
  CUDA(cudaMemcpy(device,initial.data(),6*v*sizeof(double),cudaMemcpyHostToDevice));
  cudaEvent_t start,stop;
  CUDA(cudaEventCreate(&start)); CUDA(cudaEventCreate(&stop));
  CUDA(cudaEventRecord(start));
  for(int t=0;t<steps;t++){
    magnetic<<<blocks,threads>>>(device,n,dt/h);
    electric<<<blocks,threads>>>(device,n,dt/h);
  }
  CUDA(cudaEventRecord(stop)); CUDA(cudaEventSynchronize(stop));
  float milliseconds=0; CUDA(cudaEventElapsedTime(&milliseconds,start,stop));
  std::vector<double> result(6*v);
  CUDA(cudaMemcpy(result.data(),device,6*v*sizeof(double),cudaMemcpyDeviceToHost));
  double wall_seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-wall_start).count();
  double error=0,error_e=0;
  for(int i=0;i<6*v;i++) error=std::max(error,std::abs(result[i]-reference[i]));
  for(int i=0;i<v;i++){
    double exact=std::sin(2*pi*(i/(n*n)*h-steps*dt));
    error_e+=(result[v+i]-exact)*(result[v+i]-exact);
  }
  std::vector<double> host_aos(6*v),host_soa(6*v);
  for(int i=0;i<v;i++) for(int q=0;q<6;q++){
    double value=std::sin(.01*(i+1)*(q+1));
    host_aos[6*i+q]=value;host_soa[q*v+i]=value;
  }
  CUDA(cudaMemcpy(aos,host_aos.data(),6*v*sizeof(double),cudaMemcpyHostToDevice));
  CUDA(cudaMemcpy(device,host_soa.data(),6*v*sizeof(double),cudaMemcpyHostToDevice));
  float copy_ms[2];
  for(int layout=0;layout<2;layout++){
    const double* ptr=layout?aos:device;
    component_copy<<<blocks,threads>>>(ptr,out,v,layout?6:1);
    CUDA(cudaDeviceSynchronize());
    CUDA(cudaEventRecord(start));
    for(int rep=0;rep<100;rep++) component_copy<<<blocks,threads>>>(ptr,out,v,layout?6:1);
    CUDA(cudaEventRecord(stop)); CUDA(cudaEventSynchronize(stop));
    CUDA(cudaEventElapsedTime(&copy_ms[layout],start,stop));
    std::vector<double> copied(v);
    CUDA(cudaMemcpy(copied.data(),out,v*sizeof(double),cudaMemcpyDeviceToHost));
    for(int i=0;i<v;i++) if(copied[i]!=host_soa[i]) return 5;
  }
  cudaDeviceProp properties; CUDA(cudaGetDeviceProperties(&properties,0));
  std::printf("{\"status\":\"executed_gpu\",\"gpu\":\"%s\",\"n\":%d,\"dofs\":%d,"
    "\"dtype\":\"float64\",\"steps\":%d,\"dt\":%.16g,\"T\":%.16g,"
    "\"seconds_device_advance\":%.9g,\"max_cpu_difference\":%.9g,\"error_E_L2\":%.9g,"
    "\"seconds_with_transfers\":%.9g,\"general_field_cpu_difference\":%.9g,"
    "\"soa_copy_seconds\":%.9g,\"aos_copy_seconds\":%.9g,"
    "\"layout_repeats\":100,\"threads\":%d,\"dram_bytes_measured\":null,"
    "\"flops_model\":%.0f,\"bytes_model\":%.0f,"
    "\"work_model\":\"uniform-grid dt/h fusion: 30 FLOPs/cell/step; ideal two-phase bytes\","
    "\"timing_scope\":\"events; H2D/D2H excluded; resident fields\"}\n",
    properties.name,n,6*v,steps,dt,steps*dt,milliseconds/1000.,error,std::sqrt(error_e/v),
    wall_seconds,general_error,
    copy_ms[0]/1000.,copy_ms[1]/1000.,threads,30.*v*steps,144.*v*steps);
  CUDA(cudaFree(device)); CUDA(cudaFree(aos)); CUDA(cudaFree(out));
  CUDA(cudaEventDestroy(start)); CUDA(cudaEventDestroy(stop));
  return error<1e-10?0:3;
}
