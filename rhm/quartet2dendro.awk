BEGIN {root=-1;}
/sankoff-score/ {score=strtonum($2);}
/\[label/ && !/\[label=\"f:/ {i=$1+1; split($2,fld,"\""); label[i]=fld[2]; if (i>ns) ns=i; if (OUTGROUP==label[i]) root=i; split($3,fld,"="); split(fld[2],fld,"]"); color[i]=fld[1];}
/\[label=\"f:/ {i=$1+1; label[i]="i" (i-1); if (i>ns) ns=i;}
/--/ || /->/ {n1=$1+1; n2=strtonum($3)+1; split($4,fld,"="); len=fld[2]; e[n1,++es[n1]]=n2; le[n1,es[n1]]=len; e[n2,++es[n2]]=n1; le[n2,es[n2]]=len;}
END {
  extra=-1;
  for (ni=1;ni<=ns;ni++)
    if (es[ni]==2)
      extra=ni;
  if (extra>-1)
  {
    printf "# removing interior node %s.\n", label[extra];
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
	  printf "# neighbors of %s: %s\n", label[ni], label[e[ni,ei]];

	  if (label[e[ni,ei]]==rlabel[2])
	  {
	    rootpair1=ni;
	    rootpair2=e[ni,ei];
	  }
	}
      }
  }

  printf "# adding root between %s and %s.\n",
    label[rootpair1], label[rootpair2];
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

  printf "digraph G {\n";#\trankdir=LR;\n\tranksep=3;\n\tnodesep=0.05;\n";
  printf "label=\"sankoff-score %d\";\n", score;
  printf "\tedge [style=bold dir=none];\n";

  ni=root; back[ni]=-1; ec[ni]=1;oi=1; maxlev=0;minlev=0;
  dep=0;
  while (ni!=-1)
  {
#
#      if (es[ni]==1 || ec[ni]==2)
#      {
#	for (a=1;a<=dep;a++)
#	  printf " ";
#	printf "%s(%d) %d\n", label[ni], ni, es[ni];
#      }
#
    while (e[ni,ec[ni]]==back[ni]) ec[ni]++;
    if (ec[ni]>es[ni])
    {
      #printf "%d [label=\"%s\"];\n", ni, label[ni];

      #inner nodes as close to leafs as possible
      if (back[ni]!=-1 && lev[ni]+1>lev[back[ni]])
	lev[back[ni]]=lev[ni]+1;
      if (lev[ni]+1>maxlev)
	maxlev=lev[ni]+1;
      order[oi++]=ni;
      ni=back[ni];
      dep--;
    }
    else
    {
      dep++;
      ton=e[ni,ec[ni]];
      ec[ni]++;
      back[ton]=ni;
      ec[ton]=1;
      ni=ton;
      if (length(JOINLATE)>0)
      {
        # inner nodes as close to root as possible
	lev[ni]=lev[back[ni]]-1;
	if (lev[ni]<minlev)
	  minlev=lev[ni];
      }
    }
  }

  for (ni=1;ni<=ns;ni++)
  {
#    for (ei=1;ei<=es[ni];ei++)
#      printf "%d -- %d;\n", ni, e[ni,ei];
    if (es[ni]==1)
      lev[ni]=0;
    else
      lev[ni]-=minlev;
  }
  maxlev-=minlev;

  # add extra node for outgroup
  #ns++;
  #label[ns]=label[root];
  #es[ns]=1;
  #e[ns,1]=root;
  #lev[ns]=0;
  #order[ns]=ns;

  #lev[root]=maxlev;
  #label[root]="virtual";
  #color[root]="";
  #es[root]++;
  #e[root,es[root]]=ns;

  #for (ni=1;ni<=ns;ni++)
  #  printf "%s(%d) %d %d\n", label[ni],ni, lev[ni], order[ni];

  for (li=1;li<=maxlev+1;li++)
  {
    printf "\tsubgraph %d {\n", li;
    if (li==1)
      printf "\t\tnode [shape=plaintext,width=0,align=right,margin=0.02,0];\n";
    printf "\t\trank=same;\n";
    for (oi=1;oi<=ns;oi++)
    {
      ni=order[oi];
      if (lev[ni]+1==li)
      {
	if (li==1)
	{
	  x=(lev[e[ni,1]])/3; #drag branching-points towards root
	  #x=lev[ni]/3; #all leafs at bottom level
	  y[ni]=(leaf++)/4.0;
	}
	else
	{
	  x=li/3;
	  c=0;
	  for (ei=1;ei<=es[ni];ei++)
	    if (lev[e[ni,ei]]<lev[ni])
	    {
	      y[ni]+=y[e[ni,ei]];
	      c++;
	    }
	  y[ni]/=c;
	  miny=y[ni];
	  maxy=y[ni];
	  for (ei=1;ei<=es[ni];ei++)
	    if (lev[e[ni,ei]]<lev[ni])
	    {
	      if (y[e[ni,ei]]<miny)
		miny=y[e[ni,ei]];
	      else if (y[e[ni,ei]]>maxy)
		maxy=y[e[ni,ei]];
	    }
	  height=maxy-miny;
	}
	if (li>1)
	  x+=.3;
	if (li==1)
 	{
 	  slabel=label[ni];
 	  clabel=color[ni];
 	}
 	else
 	{
 	  slabel="";
 	  clalel="";
 	}
	if (clabel)
	  colorlabel="style=filled fillcolor=" clabel;
	else
	  colorlabel="";

	x-=length(slabel)/16;
	printf "\t\tn%d [pos=\"%f,%f!\" height=%f label=\"%s\" %s];\n",
	  ni,x,y[ni],height,slabel,colorlabel;
	if (li>1)
	{
	  printf "\t\tnn%d [pos=\"%f,%f!\" height=0 style=invis label=\"\"];\n",
	    ni,x,maxy;
	  printf "\t\tns%d [pos=\"%f,%f!\" height=0 style=invis label=\"\"];\n",
	    ni,x,miny;
	}
      }
    }
    printf "\t}\n";
    if (li==1)
      printf "\tnode [shape=box width=0 fixedsize=1];\n";
  }
  for (ni=1;ni<=ns;ni++)
  {
    for (ei=1;ni!=extra&&ei<=es[ni];ei++)
      if (lev[e[ni,ei]]>lev[ni])
      {
	if (y[e[ni,ei]]<y[ni])
	  post="n";
	else
	  post="s";
	printf "\tn%d -> n%s%d;\n", ni,post,e[ni,ei];
	printf "\tn%d -> n%s%d;\n", e[ni,ei],post,e[ni,ei];
      }
  }
  printf "}\n";
}

