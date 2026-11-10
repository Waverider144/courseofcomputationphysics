// Full periodic Maxwell Yee advance with MPI slab halos and constraint diagnostics.
#include <mpi.h>
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <vector>

int main(int argc,char**argv){
  MPI_Init(&argc,&argv);
  int rank,size; MPI_Comm_rank(MPI_COMM_WORLD,&rank); MPI_Comm_size(MPI_COMM_WORLD,&size);
  int n=argc>1?std::atoi(argv[1]):24;
  if(n<4||n%size||n/size<2){MPI_Finalize();return 1;}
  int nx=n/size,plane=n*n,volume=(nx+2)*plane,left=(rank+size-1)%size,right=(rank+1)%size;
  double h=1./n,T=.5,pi=std::acos(-1.);
  int steps=static_cast<int>(std::ceil(T/(.45*h))); double dt=T/steps,s=dt/h;
  std::vector<double> f(6*volume),send(3*plane),recv(3*plane);
  auto idx=[&](int q,int x,int y,int z){return q*volume+x*plane+((y+n)%n)*n+(z+n)%n;};
  for(int x=1;x<=nx;x++) for(int y=0;y<n;y++) for(int z=0;z<n;z++){
    double gx=(rank*nx+x-1)*h;
    f[idx(1,x,y,z)]=std::sin(2*pi*gx);
    f[idx(5,x,y,z)]=std::sin(2*pi*(gx+.5*h+.5*dt));
  }
  auto exchange=[&](int first,bool forward){
    int source=forward?1:nx,target=forward?nx+1:0;
    for(int q=0;q<3;q++) std::copy_n(f.data()+(first+q)*volume+source*plane,plane,send.data()+q*plane);
    MPI_Sendrecv(send.data(),3*plane,MPI_DOUBLE,forward?left:right,first+40,
                 recv.data(),3*plane,MPI_DOUBLE,forward?right:left,first+40,MPI_COMM_WORLD,MPI_STATUS_IGNORE);
    for(int q=0;q<3;q++) std::copy_n(recv.data()+q*plane,plane,f.data()+(first+q)*volume+target*plane);
  };
  auto magnetic=[&](){
    for(int x=1;x<=nx;x++) for(int y=0;y<n;y++) for(int z=0;z<n;z++){
      f[idx(3,x,y,z)]-=s*((f[idx(2,x,y+1,z)]-f[idx(2,x,y,z)])-(f[idx(1,x,y,z+1)]-f[idx(1,x,y,z)]));
      f[idx(4,x,y,z)]-=s*((f[idx(0,x,y,z+1)]-f[idx(0,x,y,z)])-(f[idx(2,x+1,y,z)]-f[idx(2,x,y,z)]));
      f[idx(5,x,y,z)]-=s*((f[idx(1,x+1,y,z)]-f[idx(1,x,y,z)])-(f[idx(0,x,y+1,z)]-f[idx(0,x,y,z)]));
    }
  };
  auto electric=[&](){
    for(int x=1;x<=nx;x++) for(int y=0;y<n;y++) for(int z=0;z<n;z++){
      f[idx(0,x,y,z)]+=s*((f[idx(5,x,y,z)]-f[idx(5,x,y-1,z)])-(f[idx(4,x,y,z)]-f[idx(4,x,y,z-1)]));
      f[idx(1,x,y,z)]+=s*((f[idx(3,x,y,z)]-f[idx(3,x,y,z-1)])-(f[idx(5,x,y,z)]-f[idx(5,x-1,y,z)]));
      f[idx(2,x,y,z)]+=s*((f[idx(4,x,y,z)]-f[idx(4,x-1,y,z)])-(f[idx(3,x,y,z)]-f[idx(3,x,y-1,z)]));
    }
  };
  auto energy=[&](){
    exchange(0,true); double local=0,global=0;
    for(int x=1;x<=nx;x++) for(int y=0;y<n;y++) for(int z=0;z<n;z++){
      double c[3]={
        (f[idx(2,x,y+1,z)]-f[idx(2,x,y,z)])-(f[idx(1,x,y,z+1)]-f[idx(1,x,y,z)]),
        (f[idx(0,x,y,z+1)]-f[idx(0,x,y,z)])-(f[idx(2,x+1,y,z)]-f[idx(2,x,y,z)]),
        (f[idx(1,x+1,y,z)]-f[idx(1,x,y,z)])-(f[idx(0,x,y+1,z)]-f[idx(0,x,y,z)])};
      for(int q=0;q<3;q++){
        double e=f[idx(q,x,y,z)],b=f[idx(q+3,x,y,z)];
        local+=.5*h*h*h*(e*e+b*(b-s*c[q]));
      }
    }
    MPI_Allreduce(&local,&global,1,MPI_DOUBLE,MPI_SUM,MPI_COMM_WORLD);return global;
  };
  double initial=energy();
  MPI_Barrier(MPI_COMM_WORLD); double start=MPI_Wtime();
  for(int t=0;t<steps;t++){exchange(0,true);magnetic();exchange(3,false);electric();}
  double local_time=MPI_Wtime()-start,maximum=0;
  MPI_Reduce(&local_time,&maximum,1,MPI_DOUBLE,MPI_MAX,0,MPI_COMM_WORLD);
  double energy_drift=std::abs(energy()-initial)/initial;
  exchange(3,true);exchange(0,false);
  double local_error=0,global_error=0,local_div[2]={0,0},global_div[2];
  for(int x=1;x<=nx;x++) for(int y=0;y<n;y++) for(int z=0;z<n;z++){
    double exact=std::sin(2*pi*((rank*nx+x-1)*h-T));
    double error=f[idx(1,x,y,z)]-exact;
    local_error+=h*h*h*error*error;
    double db=(f[idx(3,x+1,y,z)]-f[idx(3,x,y,z)]
              +f[idx(4,x,y+1,z)]-f[idx(4,x,y,z)]
              +f[idx(5,x,y,z+1)]-f[idx(5,x,y,z)])/h;
    double de=(f[idx(0,x,y,z)]-f[idx(0,x-1,y,z)]
              +f[idx(1,x,y,z)]-f[idx(1,x,y-1,z)]
              +f[idx(2,x,y,z)]-f[idx(2,x,y,z-1)])/h;
    local_div[0]=std::max(local_div[0],std::abs(db));local_div[1]=std::max(local_div[1],std::abs(de));
  }
  MPI_Allreduce(&local_error,&global_error,1,MPI_DOUBLE,MPI_SUM,MPI_COMM_WORLD);
  MPI_Allreduce(local_div,global_div,2,MPI_DOUBLE,MPI_MAX,MPI_COMM_WORLD);
  if(!rank) std::printf("{\"status\":\"executed_mpi\",\"case\":\"full_yee\","
    "\"ranks\":%d,\"n\":%d,\"dofs\":%d,\"steps\":%d,\"dt\":%.16g,\"T\":%.16g,"
    "\"dtype\":\"float64\",\"max_rank_seconds\":%.9g,\"error_E_L2\":%.12g,"
    "\"divB_max\":%.9g,\"divE_max\":%.9g,\"modified_energy_relative_drift\":%.9g,"
    "\"flops_model\":%.0f,\"send_bytes_per_rank_step\":%d,"
    "\"scope\":\"advance includes two-phase packed halos; diagnostics excluded\"}\n",
    size,n,6*n*n*n,steps,dt,T,maximum,std::sqrt(global_error),global_div[0],global_div[1],
    energy_drift,30.*n*n*n*steps,6*plane*8);
  bool ok=energy_drift<1e-11&&global_div[0]<1e-11&&global_div[1]<1e-11&&std::isfinite(global_error);
  MPI_Finalize();return ok?0:2;
}
