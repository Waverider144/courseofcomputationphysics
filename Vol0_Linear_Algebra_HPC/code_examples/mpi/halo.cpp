// Periodic 3D seven-point operator, slab decomposition in x.
#include <mpi.h>
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <vector>

int main(int argc,char**argv){
  MPI_Init(&argc,&argv);
  int rank,size; MPI_Comm_rank(MPI_COMM_WORLD,&rank); MPI_Comm_size(MPI_COMM_WORLD,&size);
  int n=argc>1?std::atoi(argv[1]):32;
  if(n<4 || n%size || n/size<2){
    if(!rank) std::fprintf(stderr,"Require n divisible by ranks and at least two x planes per rank.\n");
    MPI_Finalize(); return 1;
  }
  int nx=n/size,plane=n*n,left=(rank+size-1)%size,right=(rank+1)%size,repeats=30;
  double pi=std::acos(-1.),h=1./n;
  std::vector<double> u((nx+2)*plane),out(nx*plane),reference(nx*plane);
  for(int x=1;x<=nx;x++) for(int y=0;y<n;y++) for(int z=0;z<n;z++){
    int global=rank*nx+x-1;
    double value=std::sin(2*pi*global/n)*std::cos(2*pi*y/n)*std::sin(2*pi*z/n);
    u[x*plane+y*n+z]=value;
    reference[(x-1)*plane+y*n+z]=-12*n*n*std::pow(std::sin(pi/n),2)*value;
  }
  auto interior=[&](int first,int last){
    for(int x=first;x<=last;x++) for(int y=0;y<n;y++) for(int z=0;z<n;z++){
      int index=x*plane+y*n+z;
      out[(x-1)*plane+y*n+z]=(u[index-plane]+u[index+plane]
        +u[x*plane+((y+n-1)%n)*n+z]+u[x*plane+((y+1)%n)*n+z]
        +u[x*plane+y*n+(z+n-1)%n]+u[x*plane+y*n+(z+1)%n]-6*u[index])/(h*h);
    }
  };
  for(int mode=0;mode<2;mode++){
    auto execute=[&](){
      if(mode==0){
        MPI_Sendrecv(u.data()+plane,plane,MPI_DOUBLE,left,10,
                     u.data()+(nx+1)*plane,plane,MPI_DOUBLE,right,10,MPI_COMM_WORLD,MPI_STATUS_IGNORE);
        MPI_Sendrecv(u.data()+nx*plane,plane,MPI_DOUBLE,right,11,
                     u.data(),plane,MPI_DOUBLE,left,11,MPI_COMM_WORLD,MPI_STATUS_IGNORE);
        interior(1,nx);
      }else{
        MPI_Request requests[4];
        MPI_Irecv(u.data(),plane,MPI_DOUBLE,left,11,MPI_COMM_WORLD,&requests[0]);
        MPI_Irecv(u.data()+(nx+1)*plane,plane,MPI_DOUBLE,right,10,MPI_COMM_WORLD,&requests[1]);
        MPI_Isend(u.data()+plane,plane,MPI_DOUBLE,left,10,MPI_COMM_WORLD,&requests[2]);
        MPI_Isend(u.data()+nx*plane,plane,MPI_DOUBLE,right,11,MPI_COMM_WORLD,&requests[3]);
        interior(2,nx-1);
        MPI_Waitall(4,requests,MPI_STATUSES_IGNORE);
        interior(1,1); interior(nx,nx);
      }
    };
    execute(); MPI_Barrier(MPI_COMM_WORLD);
    double start=MPI_Wtime();
    for(int rep=0;rep<repeats;rep++) execute();
    double local=(MPI_Wtime()-start)/repeats,maximum=0;
    MPI_Reduce(&local,&maximum,1,MPI_DOUBLE,MPI_MAX,0,MPI_COMM_WORLD);
    double error=0,global_error=0;
    for(int i=0;i<nx*plane;i++) error=std::max(error,std::abs(out[i]-reference[i]));
    MPI_Allreduce(&error,&global_error,1,MPI_DOUBLE,MPI_MAX,MPI_COMM_WORLD);
    if(!rank) std::printf("{\"status\":\"executed_mpi\",\"mode\":\"%s\",\"ranks\":%d,"
      "\"global_n\":%d,\"local_nx\":%d,\"dtype\":\"float64\",\"repeats\":%d,"
      "\"max_rank_seconds\":%.9g,\"max_error\":%.9g,\"send_bytes_per_rank\":%d,"
      "\"scope\":\"same-host slab stencil; not cross-node scaling\"}\n",
      mode?"nonblocking":"sendrecv",size,n,nx,repeats,maximum,global_error,2*plane*8);
    if(global_error>1e-9){MPI_Finalize(); return 2;}
  }
  MPI_Finalize(); return 0;
}
