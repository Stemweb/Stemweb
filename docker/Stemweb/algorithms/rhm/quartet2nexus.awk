BEGIN {root=-1;}
/sankoff-score/ {score=($2);}
/\[label/ && !/\[label=\"f:/ {i=$1+1; split($2,fld,"\""); label[i]=fld[2]; if (i>ns) ns=i; if (OUTGROUP==label[i]) root=i; split($3,fld,"="); split(fld[2],fld,"]"); color[i]=fld[1];}
/\[label=\"f:/ {i=$1+1; label[i]="i" (i-1); if (i>ns) ns=i;}
/--/ || /->/ {n1=$1+1; n2=($3)+1; split($4,fld,"="); len=fld[2]; e[n1,++es[n1]]=n2; le[n1,es[n1]]=len; e[n2,++es[n2]]=n1; le[n2,es[n2]]=len;}
END {
  extra=-1;
  for (ni=1;ni<=ns;ni++)
    if (es[ni]==2)
      extra=ni;
  if (extra>-1)
  {
    a=e[extra,1];
    b=e[extra,2];
    for (ni=1;ni<=ns;ni++)
      for (ei=1;ei<=es[ni];ei++)
	if (e[ni,ei]==extra)
	{
	  if (ni==a)
	    e[ni,ei]=b;
	  else
	    e[ni,ei]=a;
	}
    if (root==-1)
      root=a;
  }

  rootpair2=1;
  rootpair1=e[1,1];
  if (length(ROOT)>0)
  {
    split(ROOT,rlabel,":");
    for (ni=1;ni<=ns;ni++)
      if (label[ni]==rlabel[1])
      {
	for (ei=1;ei<=es[ni];ei++)
	{
	  if (label[e[ni,ei]]==rlabel[2])
	  {
	    rootpair1=ni;
	    rootpair2=e[ni,ei];
	  }
	}
      }
  }

  ns++;
  label[ns]="root";
  es[ns]=2;
  e[ns,1]=rootpair1;
  e[ns,2]=rootpair2;
  for (ei=1;ei<=es[rootpair1];ei++)
    if (e[rootpair1,ei]==rootpair2)
      e[rootpair1,ei]=ns;
  for (ei=1;ei<=es[rootpair2];ei++)
    if (e[rootpair2,ei]==rootpair1)
      e[rootpair2,ei]=ns;
  root=ns;

  ni=root; back[ni]=-1; ec[ni]=1;oi=1; maxlev=0;minlev=0;
  dep=0;
  printf "(";
  while (ni!=-1)
  {
    while (e[ni,ec[ni]]==back[ni]) ec[ni]++;
    if (es[ni]==1)
      printf label[ni];
    if (ec[ni]>es[ni])
    {
      if (es[ni]>1) printf ")";
      needcomma=1;
      ni=back[ni];
      dep--;
    }
    else
    {
      if (needcomma)
        printf ",";
      dep++;
      ton=e[ni,ec[ni]];
      ec[ni]++;
      back[ton]=ni;
      ec[ton]=1;
      ni=ton;
      if (es[ni]>1) printf "(";
      needcomma=0;
    }
  }
  printf ";\n";
}

