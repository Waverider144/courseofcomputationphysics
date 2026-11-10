// Periodic 1D high-order modal DG, upwind flux and RK4, distributed by elements.
#include <mpi.h>
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <vector>

void legendre(int p,double x,std::vector<double>& v){
  v.assign(p+1,0);v[0]=1;if(p) v[1]=x;
  for(int m=2;m<=p;m++) v[m]=((2*m-1)*x*v[m-1]-(m-1)*v[m-2])/m;
}
int main(int argc,char**argv){
  MPI_Init(&argc,&argv);
  int rank,size;MPI_Comm_rank(MPI_COMM_WORLD,&rank);MPI_Comm_size(MPI_COMM_WORLD,&size);
  int n=argc>1?std::atoi(argv[1]):16,p=argc>2?std::atoi(argv[2]):3;
  if(n%size||n<size||p<1||p>6){MPI_Finalize();return 1;}
  int cells=n/size,modes=p+1,nq=std::max(p+3,8);
  double pi=std::acos(-1.),h=1./n,T=.15;
  int steps=static_cast<int>(std::ceil(T/(.25*h/((2*p+1)*(2*p+1)))));
  double dt=T/steps;
  std::vector<double> q(nq),w(nq),basis(nq*modes),v;
  for(int j=0;j<nq;j++){
    double z=std::cos(pi*(j+.75)/(nq+.5)),derivative=0;
    for(int k=0;k<50;k++){
      legendre(nq,z,v);
      derivative=nq*(z*v[nq]-v[nq-1])/(z*z-1);
      double change=v[nq]/derivative;z-=change;
      if(std::abs(change)<1e-15) break;
    }
    legendre(nq,z,v);derivative=nq*(z*v[nq]-v[nq-1])/(z*z-1);
    q[j]=z;w[j]=2/((1-z*z)*derivative*derivative);
    legendre(p,z,v);std::copy(v.begin(),v.end(),basis.begin()+j*modes);
  }
  std::vector<double> u(cells*modes,0);
  for(int c=0;c<cells;c++) for(int j=0;j<nq;j++){
    double x=(rank*cells+c+(q[j]+1)/2)*h,value=std::sin(2*pi*x);
    for(int m=0;m<modes;m++) u[c*modes+m]+=.5*(2*m+1)*w[j]*value*basis[j*modes+m];
  }
  auto mass=[&](const std::vector<double>& state){
    double local=0,global=0;for(int c=0;c<cells;c++) local+=h*state[c*modes];
    MPI_Allreduce(&local,&global,1,MPI_DOUBLE,MPI_SUM,MPI_COMM_WORLD);return global;
  };
  auto rhs=[&](const std::vector<double>& state,std::vector<double>& result){
    std::vector<double> trace(cells,0.);
    for(int c=0;c<cells;c++) for(int m=0;m<modes;m++) trace[c]+=state[c*modes+m];
    double incoming=0;
    MPI_Sendrecv(&trace.back(),1,MPI_DOUBLE,(rank+1)%size,8,&incoming,1,MPI_DOUBLE,
                 (rank+size-1)%size,8,MPI_COMM_WORLD,MPI_STATUS_IGNORE);
    result.assign(state.size(),0.);
    for(int c=0;c<cells;c++) for(int m=0;m<modes;m++){
      double volume=0;
      for(int l=0;l<m;l++) if((m+l)%2) volume+=2*state[c*modes+l];
      double flux_left=c?trace[c-1]:incoming;
      result[c*modes+m]=(2*m+1)/h*(volume-trace[c]+(m%2?-1.:1.)*flux_left);
    }
  };
  double mass0=mass(u);
  std::vector<double> a,b,c,d,tmp(u.size());
  MPI_Barrier(MPI_COMM_WORLD);double start=MPI_Wtime();
  for(int t=0;t<steps;t++){
    rhs(u,a);
    for(size_t i=0;i<u.size();i++) tmp[i]=u[i]+.5*dt*a[i];rhs(tmp,b);
    for(size_t i=0;i<u.size();i++) tmp[i]=u[i]+.5*dt*b[i];rhs(tmp,c);
    for(size_t i=0;i<u.size();i++) tmp[i]=u[i]+dt*c[i];rhs(tmp,d);
    for(size_t i=0;i<u.size();i++) u[i]+=dt/6*(a[i]+2*b[i]+2*c[i]+d[i]);
  }
  double local_time=MPI_Wtime()-start,maximum=0;
  MPI_Reduce(&local_time,&maximum,1,MPI_DOUBLE,MPI_MAX,0,MPI_COMM_WORLD);
  double mass_drift=std::abs(mass(u)-mass0),local_error=0,global_error=0;
  for(int c0=0;c0<cells;c0++) for(int j=0;j<nq;j++){
    double value=0;for(int m=0;m<modes;m++) value+=u[c0*modes+m]*basis[j*modes+m];
    double x=(rank*cells+c0+(q[j]+1)/2)*h;
    double error=value-std::sin(2*pi*(x-T));
    local_error+=.5*h*w[j]*error*error;
  }
  MPI_Allreduce(&local_error,&global_error,1,MPI_DOUBLE,MPI_SUM,MPI_COMM_WORLD);
  if(!rank) std::printf("{\"status\":\"executed_mpi\",\"case\":\"full_dg\",\"ranks\":%d,"
    "\"elements\":%d,\"p\":%d,\"dofs\":%d,\"dtype\":\"float64\",\"steps\":%d,"
    "\"dt\":%.16g,\"T\":%.16g,\"max_rank_seconds\":%.9g,\"seconds_per_step\":%.9g,"
    "\"error_L2\":%.12g,\"mass_drift\":%.9g,\"send_bytes_per_rank_step\":32,"
    "\"scope\":\"RK4 advance includes upwind trace exchange per stage; setup excluded\"}\n",
    size,n,p,n*modes,steps,dt,T,maximum,maximum/steps,std::sqrt(global_error),mass_drift);
  bool ok=mass_drift<1e-11&&std::isfinite(global_error);
  MPI_Finalize();return ok?0:2;
}
