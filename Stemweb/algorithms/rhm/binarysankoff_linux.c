#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <assert.h>
#include <math.h>
#include <sys/time.h>
#include <sys/types.h>
#include <dirent.h>
#include <zlib.h>

//#define TEST_MODE

//#define COPY_AND_REPLACE

#define REPLACE_AMP_BY_ET
//#define REPLACE_HASH_BY_EMPTY
//#define REPLACE_DASH_BY_EMPTY
#define IGNORE_CASE
#define IGNORE_V_VS_U
#define EXACT_COPY_IS_FREE
#define EMPTY_IS_MISSING

#define QUADRATIC_TEMP

#define TIMING

#ifdef TIMING
struct timeval timer;
FILE *ftime;
void start_timer(void);
int get_timer(void);
#endif

struct node_st {
  int id, *fill;
  int *cost;
  struct node_st **array;
  struct node_st *left;
  struct node_st *right;
  struct node_st *up;
  int leftcost;
  int rightcost;
};

char gfilepath[512];
char *outfolder = "output-directory";
char *outfilename = "output_file_name";
int imax;

FILE *fout;
struct node_st *tree;
char **names;
int *Kyx, *Kx, minval, bestval;
int boot, strap, n, leafs, chunks, *empty, *unique, *bootw = NULL;
const int chunksize = 10;
const int GZIP_HEADER = 6;
int alternate = 0;


void usage(char *cmd)
{
  fprintf(stderr, "usage: %s <directory> <iterations> <bootstrap>\n\tdirectory -- texts (remember to align)\n\titerations -- simulated annealing iterations\n\tbootstrap -- how many bootstrap repetitions? 1 -> no bootstrap\nOutput goes to 'sankoff-tree_i.dot for i=0,...,<bootstrap-1>.\n", cmd);
  exit(-1);
}



unsigned int set_random_seed(void)
{
  struct timeval time;
  unsigned int seed;

  gettimeofday(&time, NULL);

  seed = (unsigned int) time.tv_usec +
        (unsigned int) time.tv_sec;

  srand(seed);

  return seed;
}

char *fullname(const char *dirname, const char *fname)
{
  static char pathfname[256];

  sprintf(pathfname, "%s/%s", dirname, fname);
  if (strlen(pathfname) > 255)
    fprintf(stderr, "OUTCH!\n");

  return pathfname;
}

int count_lines(const char *fname)
{
  FILE *f;
  int line;
  char tmp[4096];

  f = fopen(fname, "r");
  assert(f != NULL);

  line = 0;
  fgets(tmp, 4096, f);
  while (!feof(f))
  {
    line++;
    fgets(tmp, 4096, f);
  }

  fclose(f);

  return line;
}

int isempty(char *str)
{
  while (*str)
  {
    if (!isspace(*str)) return 0;
    str++;
  }
  return 1;
}

int count_words(char *str)
{
  int c = 0;

  while (*str)
  {
    c++;
    while (*str && !isspace(*str)) str++;
    while (*str && isspace(*str)) str++;
  }

  return c;
}

void mysort(char **a, int c)
{
  int i, j;
  char *tmp;

  for (i = 0; i < c-1; i++)
    for (j = i+1; j < c; j++)
      if (strcmp(a[i], a[j]) > 0)
      {
	tmp = a[i];
	a[i] = a[j];
	a[j] = tmp;
      }
}

int mystrcmp(const void *a, const void *b)
{
  return strcmp((char*)a,(char*)b);
}

char *sort_string(char *str)
{
  char **a, *buf, *ptr;
  int i = 0, c;

  c = count_words(str);
  if (c < 1)
    return str;
  buf = (char *) malloc(sizeof(char) * (strlen(str)+1));
  a = (char **) malloc(sizeof(char *) * c);

  ptr = str;
  while (*ptr)
  {
    a[i] = ptr;
    i++;
    while (*ptr && !isspace(*ptr)) ptr++;
    if (*ptr) {*ptr = '\0'; ptr++;}
    while (*ptr && isspace(*ptr)) ptr++;
  }

  mysort(a, c);

  ptr = buf;
  for (i = 0; i < c; i++)
  {
    if (ptr > buf)
      *(ptr++) = ' ';
    strcpy(ptr, a[i]);
    ptr += strlen(ptr);
  }
  strcpy(str, buf);

  free(a);
  free(buf);
  
  return str;
}

char *str_tolower(char *str)
{
  char *ptr = str;

  while (*ptr)
  {
    *ptr = tolower(*ptr);
    ptr++;
  }

  return str;
}

char *str_vtou(char *str)
{
  char *ptr = str;

  while (*ptr)
  {
    if (*ptr == 'v')
      *ptr = 'u';
    if (*ptr == 'V')
      *ptr = 'U';
    ptr++;
  }

  return str;
}

int read_file(const char *dirname)
{
  DIR *dir;
  FILE *f1, *f2;
  gzFile gfile;
#define BUFMAX 8192
  char buf[BUFMAX];
  struct dirent *de;
  int bufpos1, bufpos2, lines, f1i, f2i, ch, line;
  long f1offset;

  leafs = 0;
  names = (char **) malloc(sizeof(void *) * 1000);
  dir = (DIR *) opendir(dirname);
  while ((de = readdir(dir)))
  {
    if (de->d_name[0] != '.')
    {
      names[leafs] = (char *) malloc(sizeof(char) * (strlen(de->d_name)+1));
      strcpy(names[leafs], de->d_name);
      printf("%s ", names[leafs]);
      leafs++;
    }
  }
  printf("\n");
  closedir(dir);

  lines = count_lines(fullname(dirname, names[0]));

#ifdef TEST_MODE
  if (lines > 100) lines = 100;
#endif

  chunks = (lines-1)/chunksize+1;
  printf("%d files, %d lines, %d chunks of size %d each.\n",
	 leafs, lines, chunks, chunksize);

  Kyx = (int *) malloc(sizeof(int) * leafs * leafs * chunks);   assert(Kyx);
  Kx = (int *) malloc(sizeof(int) * leafs * chunks);            assert(Kx);
  empty = (int *) malloc(sizeof(int) * leafs * chunks);         assert(empty);
  unique = (int *) malloc(sizeof(int) * leafs * chunks);        assert(unique);
  
  for (f1i = 0; f1i < leafs; f1i++)
  {
    f1 = fopen(fullname(dirname, names[f1i]), "r");
    assert(f1);

    for (ch = 0; ch < chunks; ch++)
    {
      Kx[f1i*chunks+ch] = -1;
      empty[f1i*chunks+ch] = 1;
      unique[f1i*chunks+ch] = 1;
    }

    for (f2i = 0; f2i < leafs; f2i++)
    {
      fseek(f1, 0, SEEK_SET);

      if (f2i != f1i)
	f2 = fopen(fullname(dirname, names[f2i]), "r");
      else
	f2 = f1;
      assert(f2);
      
      for (ch = 0; ch < chunks; ch++)
      {
	f1offset = ftell(f1);
	bufpos1 = 0;
	gfile = gzopen("tmp.gz", "wb");
	for (line = 0; !feof(f1) && line < chunksize; line++)
	{
	  if (bufpos1 > 0 && buf[bufpos1-1] == '\n')
	    buf[bufpos1-1] = ' ';
	  fgets(buf+bufpos1, 2048-bufpos1, f1);
#ifdef REPLACE_AMP_BY_ET
	  if (!strcmp(buf+bufpos1, "&\n"))
	    strcpy(buf+bufpos1, "et\n");
#endif
	  if (buf[bufpos1] && buf[bufpos1] != '\n')
	    empty[f1i*chunks+ch] = 0;
#ifdef REPLACE_HASH_BY_EMPTY
	  if (!strcmp(buf+bufpos1, "#\n"))
	    strcpy(buf+bufpos1, "\n");
#endif
#ifdef REPLACE_DASH_BY_EMPTY
	  if (!strcmp(buf+bufpos1, "-\n"))
	    strcpy(buf+bufpos1, "\n");
#endif
	  bufpos1 += strlen(buf+bufpos1);
	}
	buf[bufpos1] = '\0';

	bufpos1 = strlen(buf);

	if (!bufpos1 || buf[bufpos1-1] != '\n')
	  buf[bufpos1++]='\n';
	buf[bufpos1] = '\0';
#ifdef IGNORE_CASE
	str_tolower(buf);
#endif
#ifdef IGNORE_V_VS_U
	str_vtou(buf);
#endif

	if (Kx[f1i*chunks+ch] == -1)
	{
	  gzputs(gfile, buf);
	  gzflush(gfile, Z_SYNC_FLUSH);
	
	  Kx[f1i*chunks+ch] = 
	    (int) gzoffset(gfile) - GZIP_HEADER;
	  //fprintf(stderr, "%sKx=%d\n", buf,Kx[f1i * chunks + ch]);
	  gzclose(gfile);
	  gfile = gzopen("tmp.gz", "wb");
	}

	if (f2 == f1)
	  fseek(f1, f1offset, SEEK_SET);
	bufpos2 = bufpos1;
	for (line = 0; !feof(f2) && line < chunksize; line++)
	{
	  if (bufpos2 > bufpos1 && buf[bufpos2-1] == '\n')
	    buf[bufpos2-1] = ' ';
	  fgets(buf+bufpos2, BUFMAX-bufpos2, f2);
#ifdef REPLACE_AMP_BY_ET
	  if (!strcmp(buf+bufpos2, "&\n"))
	    strcpy(buf+bufpos2, "et\n");
#endif
#ifdef REPLACE_HASH_BY_EMPTY
	  if (!strcmp(buf+bufpos2, "#\n"))
	    strcpy(buf+bufpos2, "\n");
#endif	  
	  bufpos2 += strlen(buf+bufpos2);
	}
	if (bufpos2==bufpos1 || buf[bufpos2-1] != '\n')
	  buf[bufpos2++]='\n';
	buf[bufpos2] = '\0';
#ifdef IGNORE_CASE
	str_tolower(buf+bufpos1);
#endif
#ifdef IGNORE_V_VS_U
	str_vtou(buf+bufpos1);
#endif

	bufpos2 = bufpos1+strlen(buf+bufpos1);

	if (
#ifdef EXACT_COPY_IS_FREE
	    strncmp(buf, buf+bufpos1, bufpos2/2)
#else
	    1
#endif
	    )
	{
	  gzputs(gfile, buf);
	  gzflush(gfile, Z_SYNC_FLUSH);

	  Kyx[f1i*leafs*chunks + f2i*chunks + ch] = 
	    (int) gzoffset(gfile) -
	    Kx[f1i * chunks + ch] - GZIP_HEADER;
	}
	else
	{
	  Kyx[f1i*leafs*chunks + f2i*chunks + ch] = 0;
	}

	if (!strncmp(buf, buf+bufpos1, bufpos2/2) && f2i<f1i)
	  unique[f2i*chunks+ch] = 0;  // this isnt't a new value in locus (chunk) ch
	else
	  if (0 && ch == 9) 
	    printf("%s vs %s: %d\n", names[f1i], names[f2i], Kyx[f1i*leafs*chunks + f2i*chunks + ch]);


	gzclose(gfile);      
      } 

      if (f2i != f1i)
	fclose(f2);
    }
    fprintf(stderr, ".");
    fclose(f1);
  }
  fprintf(stderr, "\n");

  f2i = 0;
  for (ch = 0; ch < chunks; ch++)
    for (f1i = 0; f1i < leafs; f1i++)
      if (unique[f1i*chunks+ch])
	f2i++;

  printf("%d/%d unique.\n", f2i, ch*leafs);
  printf("%dx%dx%d information array ready (#%p).\n", leafs, leafs, chunks, Kyx);

  /*
  for (f1i = 0; f1i < leafs; f1i++)
  {
    Kx[f1i*chunks + ch] *= 2;
    for (f2i = f1i+1; f2i < leafs; f2i++)
      for (ch = 0; ch < chunks; ch++)
      {
	Kyx[f1i*leafs*chunks + f2i*chunks + ch] =
	  Kyx[f2i*leafs*chunks + f1i*chunks + ch] =
	  Kyx[f1i*leafs*chunks + f2i*chunks + ch] +
	  Kyx[f2i*leafs*chunks + f1i*chunks + ch];
      }
  }
  */
  printf("symmetric: %d %d\n", 
	 Kyx[3*leafs*chunks + 4*chunks],
	 Kyx[4*leafs*chunks + 3*chunks]);
  /**/

  return leafs;
}

#ifdef TIMING
void start_timer(void)
{
  gettimeofday(&timer, NULL);
}

int get_timer(void)
{
  struct timeval end;

  gettimeofday(&end, NULL);

  return (int)((end.tv_sec-timer.tv_sec)*1000 + (end.tv_usec-timer.tv_usec)/1000);
}
#endif

struct node_st *new_node(int i)
{
  struct node_st *new;

  new = (struct node_st *) malloc(sizeof(struct node_st));
  new->id = i;
  new->fill = (int *) malloc(sizeof(int) * chunks);
  new->left = NULL;
  new->right = NULL;
  new->up = NULL;

  return new;
}

void free_subtree(struct node_st *node)
{
  if (node)
  {
    free_subtree(node->left);
    free_subtree(node->right);
    free(node->fill);
    free(node);
  }
}

void free_tree(struct node_st *tree)
{
  free(tree->array);
  if (tree->cost) free(tree->cost);
  free_subtree(tree);
}

struct node_st *copy_subtree(struct node_st *src, struct node_st **array)
{
  struct node_st *node;

  if (!src)
    return NULL;
  node = new_node(src->id);
  array[node->id] = node;
  node->array = array;
  node->left = copy_subtree(src->left, array);
  if (node->left)
    node->left->up = node;
  node->right = copy_subtree(src->right, array);
  if (node->right)
    node->right->up = node;

  return node;
}

struct node_st *copy_tree(struct node_st *src)
{
  struct node_st *new_tree, **array;

  array = (struct node_st **) malloc(sizeof(void *) * n);
  new_tree = copy_subtree(src, array);
  if (!src->cost)
    new_tree->cost = NULL;
  else
  {
    new_tree->cost = (int *) malloc(sizeof(int) * n*leafs*chunks*2);
    memcpy(new_tree->cost, src->cost, sizeof(int) * n*leafs*chunks*2);
  }

  return new_tree;
}

void init_bootstrap()
{
  int ch, i;

  if (!bootw)
    bootw = (int *) malloc(sizeof(int) * chunks);
  for (ch = 0; ch < chunks; ch++)
    bootw[ch] = 0;
  for (ch = 0; ch < chunks; ch++)
  {
    if (strap == 1)
      i = ch;
    else
    {
      i = -1;
      while (i < 0 || i >= chunks)
	i = (int) ((float)chunks*rand()/(RAND_MAX+1.0));
    }
    bootw[i]++;
  }

  if (strap > 1)
    fprintf(stderr, "bootstrap (%d repetitions) initialized.\n", strap);
  else
    fprintf(stderr, "no bootstrap.\n");
}

void init_tree()
{
  struct node_st *new, **array;
  int i, *permut, pi;

  fprintf(stderr, "initializing tree...\n");

  tree = NULL;
  array = (struct node_st **) malloc(sizeof(void *) * (2*leafs-1));
  permut = (int *) malloc(sizeof(int) * leafs);
  for (i = 0; i < leafs; i++)
    permut[i] = i;
  n = leafs;

  for (i = 0; i < leafs; i++)
  {
    /*
    switch (i)
    {
      case 0: pi = 21; break; // BA
      case 1: pi = 34; break; // BS
      case 2: pi = 27; break; // P
      case 3: pi = 31; break; // O
      case 4: pi = 29; break; // B
      case 5: pi = 8; break; // JG
      case 6: pi = 5; break; // BLu
      case 7: pi = 19; break; // BL
      case 8: pi = 4; break; // NR2
      case 9: pi = 16; break; // JB
      default: pi = (int) ((float)(leafs-i)*rand()/(RAND_MAX+1.0));
    }
    */
    pi = (int) ((float)(leafs-i)*rand()/(RAND_MAX+1.0));
    new = new_node(permut[pi]);
    permut[pi] = permut[leafs-i-1];
    new->array = array;
    array[new->id] = new;
    if (!tree)
    {
      new->up = new_node(n++);
      new->up->array = array;
      array[new->up->id] = new->up;
      new->up->right = new;
      tree = new->up;
    }
    else
    {
      if (!tree->left)
      {
	tree->left = new;
	new->up = tree;
      }
      else
      {
	new->up = new_node(n++);
	new->up->array = array;
	array[new->up->id] = new->up;
	new->up->left = new;
	new->up->right = tree;
	tree->up = new->up;
	tree = new->up;
      }
    }
  }
  tree->cost = NULL;
  free(permut);
  fprintf(stderr, "tree with %d nodes initialized.\n", n);

#ifdef TIMING
  fprintf(ftime, "tree initialized: %.1f ms\n", 1.0*get_timer());
#endif
}

int edge_label(struct node_st *a, struct node_st *b)
{
  int ch, sum, ab, ba;

  sum = 0;
  for (ch = 0; ch < chunks; ch++)
  {
    if (bootw[ch])
    {
      ab = Kyx[a->fill[ch]*leafs*chunks + b->fill[ch]*chunks + ch];
      ba = Kyx[b->fill[ch]*leafs*chunks + a->fill[ch]*chunks + ch];
      if (ab < ba) sum += ab;
      else sum += ba;
    }
  }

  return sum;
}

double edge_length(struct node_st *a, struct node_st *b)
{
  int leafpenalty = 0;

  //  return 0.7;

  if (!b->left && !b->right)
    leafpenalty = 0;
  leafpenalty = -1;
  return ((double)(edge_label(a, b)+leafpenalty+1))/60.0;
}

void print_subtree(struct node_st *node)
{
  char *look, *color, *name;
  int ch;

  if (!node)
    return;

  print_subtree(node->left);
  print_subtree(node->right);

  if (node->id < leafs)
    name = names[node->id];
  else
    name = NULL;
  if (!node->up)
  {
    if (node->left && node->right)
      fprintf(fout, "%d -- %d [len=%.4f];\n", node->left->id, node->right->id,
	      edge_length(node, node->left));
    return;
  }

  look = "";
  if (node->id >= leafs)
    color = "";
#ifdef HENRIK_COLORS
  else if (name && (!strcmp(name, "A") || !strcmp(name, "Ab") || 
		    !strcmp(name, "Fg") || !strcmp(name, "H") ||
		    !strcmp(name, "Ho") || !strcmp(name, "I") ||
		    !strcmp(name, "K") || !strcmp(name, "N") ||
		    !strcmp(name, "R") || !strcmp(name, "S") ||
		    !strcmp(name, "T")))
    color = " fillcolor=lightblue"; // Finland
  else if (name && (!strcmp(name, "B") || !strcmp(name, "JG") ||
		    !strcmp(name, "FRA")))
    color = " fillcolor=khaki"; // Central Europe
  else if (name && (!strcmp(name, "AJ") || 
		    !strcmp(name, "D") || !strcmp(name, "E") ||
		    !strcmp(name, "F") || !strcmp(name, "G") ||
		    !strcmp(name, "JB") || !strcmp(name, "Li") ||
		    !strcmp(name, "LT") || !strcmp(name, "MN") ||
		    !strcmp(name, "NR") || !strcmp(name, "NR2") ||
		    !strcmp(name, "Y") || !strcmp(name, "CP")))
    color = " fillcolor=darkorange"; // Vadstena
  else
    color = " fillcolor=darkolivegreen1"; // other (mostly Sweden)
#else
  color = " fillcolor=oldlace";
#endif
  if (node->id < leafs)
    fprintf(fout, "%d [label=\"%s\"%s%s];\n", 
	    node->id, names[node->id], look, color);
  else
  {
    fprintf(fout, "%d [label=\"%s:", node->id,
	    node->id<leafs ? names[node->id] : "f");
    for (ch = 0; ch < chunks; ch++)
      if (bootw[ch])
      {
	if (empty[node->fill[ch]*chunks+ch])
	  fprintf(fout, "%s-", ch?(ch==chunks/2?"\\n":":"):"");
	else
	  fprintf(fout, "%s%s", ch?(ch==chunks/2?"\\n":":"):"", 
		  names[node->fill[ch]]);
      }
      else
	fprintf(fout, "%s_", ch?(ch==chunks/2?"\\n":":"):"");
    fprintf(fout, "\"%s];\n", look);
  }
  
  if (node->left)
    fprintf(fout, "%d -- %d [len=%.4f];\n", node->id, node->left->id,
	    edge_length(node, node->left));
  if (node->right)
    fprintf(fout, "%d -- %d [len=%.4f];\n", node->id, node->right->id,
	    edge_length(node, node->right));
}

void open_output()
{
  char fname[256];
  sprintf(fname, "sankoff-tree_%d.dot", boot);
  fout = fopen(fname, "w+");
}

void close_output()
{
  fclose(fout);
}

int depth(struct node_st *node)
{
  int dl, dr;

  if (!node)
    return 0;
  dl = depth(node->left);
  dr = depth(node->right);
  if (dl > dr)
    return dl+1;
  else
    return dr+1;
}

void make_look_nice(struct node_st *node)
{
  struct node_st *tmp;

  if (!node)
    return;

  if (depth(node->left) < depth(node->right))
  {
    tmp = node->left;
    node->left = node->right;
    node->right = tmp;
  }

  make_look_nice(node->left);
  make_look_nice(node->right);
}

void print_tree(struct node_st *tree)
{
  int ch;
  //fprintf(stderr, ".");
  make_look_nice(tree);
  open_output();
  fprintf(fout, "graph \"sankoff-tree\" {\nlabel=\"sankoff-score %d ", 
	  bestval);
  fprintf(fout, "bootstrap ");
  if (strap == 1)
    fprintf(fout, "off");
  else
    for (ch = 0; ch < chunks; ch++)
      fprintf(fout, "%s%d", ch?",":"", bootw[ch]);
  fprintf(fout, "\";\n");
  fprintf(fout, "edge [style=bold];\nnode[shape=plaintext fontsize=20];\n");
  print_subtree(tree);
  fprintf(fout, "}\n");
  close_output();
}

void free_mem()
{
  int i;
  free(bootw);
  for (i = 0; i < leafs; i++)
    free(names[i]);
  free(names);
  free(empty);
  free(unique);
  free(Kx);
  free(Kyx);
}

int min_cost(int *cost, int id, int i, int ch)
{
  int j, val, minval;

  if (!unique[i*chunks+ch])
    return RAND_MAX/256;

  if (id < leafs)
  {
#ifdef EMPTY_IS_MISSING
    if (empty[id*chunks+ch])
      return 0;
    else
#endif
      return Kyx[i*leafs*chunks+id*chunks+ch];
  }

  minval = -1;

  for (j = 0; j < leafs; j++)
  {
    if (unique[j*chunks+ch])
    {
      val = cost[j*chunks+ch] + Kyx[i*leafs*chunks+j*chunks+ch];
      if (val < minval || minval == -1)
	minval = val;
    }
  }
  
  return minval;
}

int eval_subtree(int *cost, struct node_st *node, int ch)
{
  int i, minval = 0;

  if (node->left && node->right)
  {
    eval_subtree(cost, node->left, ch);
    eval_subtree(cost, node->right, ch);
    
    for (i = 0; i < leafs; i++)
    {
      cost[node->id*leafs*chunks+i*chunks+ch] = 
	min_cost(cost+node->left->id*leafs*chunks, node->left->id, i, ch) +
	min_cost(cost+node->right->id*leafs*chunks, node->right->id, i, ch);
      if (i == 0 || isinf((float) minval) || 
	  cost[node->id*leafs*chunks+i*chunks+ch] < minval)
	minval = cost[node->id*leafs*chunks+i*chunks+ch];
    }
  }
  else
  {
    for (i = 0; i < leafs; i++)
      if (i == node->id)
	cost[node->id*leafs*chunks+i*chunks+ch] = 0.0;
      else
	cost[node->id*leafs*chunks+i*chunks+ch] = RAND_MAX/256;
    minval = 0.0;
  }

  return minval;
}

int eval_uptree(struct node_st *tree, struct node_st *node, 
		struct node_st *stopper, int ch)
{
  int i, minval = 0, *cost;

  cost = tree->cost;

  if (!node)
    node = tree;

  if (node->left && node->right)
  {
    for (i = 0; i < leafs; i++)
    {
      cost[node->id*leafs*chunks+i*chunks+ch] = 
	min_cost(cost+node->left->id*leafs*chunks, node->left->id, i, ch) +
	min_cost(cost+node->right->id*leafs*chunks, node->right->id, i, ch);
      if (i == 0 || isinf((float) minval) || 
	  cost[node->id*leafs*chunks+i*chunks+ch] < minval)
	minval = cost[node->id*leafs*chunks+i*chunks+ch];
    }
  }
  else
  {
    for (i = 0; i < leafs; i++)
      if (i == node->id)
	cost[node->id*leafs*chunks+i*chunks+ch] = 0.0;
      else
	cost[node->id*leafs*chunks+i*chunks+ch] = RAND_MAX/256;
    minval = 0;
  }

  if (node->up && node->up != stopper)
    return eval_uptree(tree, node->up, stopper, ch);
  else
    return minval;
}

void store_cost_uptree(struct node_st *tree, struct node_st *node)
{
  int ch, i;

  while (node)
  {
    for (ch = 0; ch < chunks; ch++)
      if (bootw[ch])
	for (i = 0; i < leafs; i++)
	  tree->cost[(n+node->id)*leafs*chunks + i*chunks+ch] =
	    tree->cost[node->id*leafs*chunks + i*chunks+ch];
    node = node->up;
  }
}

void restore_cost_uptree(struct node_st *tree, struct node_st *node)
{
  int ch, i;

  while (node)
  {
    for (ch = 0; ch < chunks; ch++)
      if (bootw[ch])
	for (i = 0; i < leafs; i++)
	  tree->cost[node->id*leafs*chunks + i*chunks+ch] =
	    tree->cost[(n+node->id)*leafs*chunks + i*chunks+ch];
    node = node->up;
  }
}

void fill_subtree(int *cost, struct node_st *node)
{
  int i, ch;
  int val, minval = 0;

  if (!node) return;

  for (ch = 0; ch < chunks; ch++)
  {
    if (bootw[ch])
      for (i = 0; i < leafs; i++)
      {
	if (node->up)
	  val = Kyx[node->up->fill[ch]*leafs*chunks+i*chunks+ch];
	else
	  val = Kx[i*chunks+ch];
	val += cost[node->id*leafs*chunks+i*chunks+ch];
	/*
	  if (node == node->array[19]->up && ch == 0 && 
	  (i < 8 || isinf(minval) || val < minval))
	  printf("for %d at %d, %d('%s%s') takes %d bytes.\n",
	  node->id, ch, i, names[i], empty[i*chunks+ch]?"/-":"", val);
	*/
	if (i == 0 || isinf((float) minval) || val < minval)
	{
	  minval = val;
	  node->fill[ch] = i;
	}
      }
  }

  fill_subtree(cost, node->left);
  fill_subtree(cost, node->right);
}

int  level(struct node_st *tree, struct node_st *node)
{
  int lev = 0;

  while (node && node != tree)
  {
    node = node->up;
    lev++;
  }

  return lev;
}

int eval_tree(struct node_st *tree, struct node_st *ra,
		 struct node_st *rb)
{
  int value, ch, leva, levb;
  struct node_st *aup, *bup, *stopper;

  if (!tree->cost)
  {
    tree->cost = (int *) malloc(sizeof(int) * n*leafs*chunks*2);
    ra = rb = NULL;
  }

  value = 0.0;
  for (ch = 0; ch < chunks; ch++)
  {
    if (bootw[ch])
    {
      if (!ra && !rb)
	value += bootw[ch]*eval_subtree(tree->cost, tree, ch);
      else
      {
	leva = level(tree, ra);
	levb = level(tree, rb);
	aup = ra; bup = rb;
	while (leva > levb && aup)
	{
	  aup = aup->up;
	  leva--;
	}
	while (levb > leva && bup)
	{
	  bup = bup->up;
	  levb--;
	}
	while (aup && bup && aup != bup)
	{
	  aup = aup->up;
	  bup = bup->up;
	}
	if (aup == bup) 
	  stopper = aup;
	else
	  stopper = NULL;
	
	eval_uptree(tree, ra, stopper, ch); // not yet fully updated
	// after second call to eval_uptree, add updated value
	value += bootw[ch]*eval_uptree(tree, rb, NULL, ch); 
      }
    }
  }

  return value;
}

int same_branch(struct node_st *a, struct node_st *b)
{
  struct node_st *node;

  if (a == b) return 1;

  node = a;
  while ((node = node->up))
    if (node == b)
      return 1;

  node = b;
  while ((node = node->up))
    if (node == a)
      return 1;

  return 0;
}

struct node_st *do_mutate_tree(struct node_st *tree, 
			       struct node_st *a,
			       struct node_st *b)
{
  struct node_st *tmp;

  //oldcost = eval_tree(tree, *unra, *unrb);

  //fprintf(stderr, "1.1.1 #%d #%d #%d\n", (int)tree, (int)a, (int)b);
  //fprintf(stderr, "1.1.2 #%d #%d\n", (int)a->up, (int)b->up);

  if (alternate)
  {
    if (a->up->left == a)
      a->up->left = b;
    else 
      a->up->right = b;
    if (b->up->left == b)
      b->up->left = a;
    else
      b->up->right = a;
    
    tmp = a->up;
    a->up = b->up;
    b->up = tmp;

    //if (eval_tree(tree, *unra, *unrb) < oldcost)
    //  printf("improved by exchange (was %d).\n", oldcost);
  }
  else
  {
    /*
    fprintf(stderr, 
	    "take %d with parents %d:%d (sibling %d) and move under %d with %d.\n",
	    a->id, a->up->id, a->up->up?a->up->up->id:-1,
	    a->up->left==a?a->up->right->id:a->up->left->id,
	    b->up->id, b->id);
    */

    if (a->up->left == a)
      tmp = a->up->right;
    else
      tmp = a->up->left;
    tmp->up = a->up->up;

    if (a->up->up)
    {
      if (a->up->up->left == a->up)
	a->up->up->left = tmp;
      else
	a->up->up->right = tmp;
    }
    else
    {
      //fprintf(stderr, "%d was root, now %d.\n", a->up->id, tmp->id);
      tmp->cost = tree->cost;
      tree = tmp;
    }

    tmp = b->up;
    b->up = a->up;
    a->up->up = tmp;
    
    //fprintf(stderr, "node %d now under %d.\n", a->up->id, a->up->up->id);

    if (tmp->left == b)
      tmp->left = a->up;
    else
      tmp->right = a->up;

    a->up->left = b;
    a->up->right = a;

    //fprintf(stderr, "%d now under %d with %d (under %d).\n",
    //    a->id, a->up->id, b->id, b->up->id);

    //  if (eval_tree(tree, *unra, *unrb) < oldcost)
    //  printf("improved by joining (was %d).\n", oldcost);
  }      

  //fprintf(stderr, "1.1.x\n");

  return tree;
}

struct node_st *prep_mutate_tree(struct node_st *tree, 
				 struct node_st **a,
				 struct node_st **b,
				 struct node_st **ra,
				 struct node_st **rb)
{
  int i, j;

  alternate = !alternate;
  //  alternate = 0;

  while (1)
  {
    i = (int) ((float)n*rand()/(RAND_MAX+1.0));
    j = (int) ((float)(n-1)*rand()/(RAND_MAX+1.0)); if (j == i) j++;
    if (i < 0 || i >=n || j < 0 || j >= n) continue;
    *a = tree->array[i];
    *b = tree->array[j];
    if ((*a)->up && (*b)->up && !same_branch(*a, *b) && 
	((*a)->up != (*b)->up) &&
	(alternate || ((*a)->up->up && (*b)->up->up)))
      break;
  }

  //fprintf(stderr, "1.1 #%d #%d #%d\n", (int)tree, (int)a->up, (int)b->up);

  //
  if (alternate)
  {
    *ra = *a;
    *rb = *b;
  }
  else
  {
    *ra = *a;
    if ((*a)->up->left == *a)
      *rb = (*a)->up->right;
    else
      *rb = (*a)->up->left;
  }

  return tree;
}

float my_exp(float x)
{
  if (x < -3.25)
    return 0.0;

  x += 3.25;
  return x*x/10.5625;
}

int optimize_tree(int iters)
{
  int newval, iter, postpone = 10;
  float T, dif;
  static struct node_st *new_tree;
  struct node_st *ra, *rb, *a, *b;
#ifndef QUADRATIC_TEMP
  double alpha;
  alpha = pow(0.05, 1.0/(double)iters);
  fprintf(stderr, "alpha %f.\n", alpha);
#endif

  fprintf(stderr, "running %d iterations\n\n", iters);

  T = 10.0;

  iter = 0;
  bestval = minval = eval_tree(tree, NULL, NULL);
  fill_subtree(tree->cost, tree);
  print_tree(tree);

  while (iter++ < iters)
  {
    if (iter > .95*iters)
      T = 0.0;
    else
#ifdef QUADRATIC_TEMP
      T = 1.0-(float)iter/(float)iters;
    T *= 5.0*T;
#else
    T = T*alpha;
#endif
#ifdef COPY_AND_REPLACE
    new_tree = prep_mutate_tree(copy_tree(tree), &a, &b, &ra, &rb);
    do_mutate_tree(new_tree, a, b);
#else
    new_tree = prep_mutate_tree(tree, &a, &b, &ra, &rb);
    store_cost_uptree(new_tree, a);
    store_cost_uptree(new_tree, b);
    do_mutate_tree(tree, a, b);
#endif
    newval = eval_tree(new_tree, ra, rb);
    if (newval <= minval 
	|| (T > 0.0 && (dif=(float)(minval-newval)/T)>-10.0 &&
	    drand48() < exp(dif)))
    {
#ifdef COPY_AND_REPLACE
      free_tree(tree);
      tree = new_tree;
#endif
      //fprintf(stderr, "accept(%d).\n", alternate);
      if (newval < bestval)
      {
	bestval = newval;
#ifdef TIMING
	int local_timer = get_timer();
#endif
	fill_subtree(tree->cost, tree);
#ifdef TIMING
	fprintf(ftime, "inference time %d ms\n", get_timer()-local_timer);
#endif
	print_tree(tree);
	postpone = 0;
      }
      minval = newval;
    }
    else
    {
#ifdef COPY_AND_REPLACE
      free_tree(new_tree);
#else
      // fprintf(stderr, "revert(%d) %d %d.\n", alternate, ra->id, rb->id);
      do_mutate_tree(tree, ra, rb);
      restore_cost_uptree(tree, a);
      restore_cost_uptree(tree, b);
#endif
    }

    if (!postpone)
    {
      fprintf(stderr, 
	      "\033[1A\033[80Dbest score %d now %d (iter %d/%d temp %.2f).\n", 
	      bestval, minval, iter, iters, T);
#ifdef TIMING
      fprintf(ftime, "%d iterations: %.1f s\n", iter, get_timer()/1000.0);
#endif
    }
    if (--postpone < 0)
      postpone = 250;
  }

#ifdef TIMING
  fprintf(ftime, "optimization finished: %.1f s\n", get_timer()/1000.0);
#endif
  
  return bestval;
}

int main(int argc, char *argv[])
{
  set_random_seed();
  
  if (argc < 4)
    usage(argv[0]);

#ifdef TIMING
  ftime = fopen("timing.txt", "w");
  start_timer();
#endif
  fprintf(stderr, "check 1\n");

  read_file(argv[1]);
  fprintf(stderr, "check 2\n");
  strap = atoi(argv[3]);

  fprintf(stderr, "check 3\n");
  for (boot = 0; boot < strap; boot++)
  {
    init_bootstrap();
    init_tree();
    optimize_tree(atoi(argv[2]));
    free_tree(tree);
  }
  free_mem();

#ifdef TIMING
  fclose(ftime);
#endif

  return 0;
}


/*
 *	 wrapper for using this module from python.
 */

static PyObject* method_binsankoff(PyObject* self, PyObject* args)
{
  char numstr[10];
  char *infolder = NULL; /* input path, optionally including input-filename */

  if(!PyArg_ParseTuple(args, "isssi", &strap, &infolder, &outfolder, &outfilename, &imax)) {
  
        fprintf(stderr, "py_main +++++++++++++++  PyArg_ParseTuple() failed ++++++++++++++++++\n");
        return PyLong_FromLong(-1);
  }

	set_random_seed();  
  read_file(infolder);
	sprintf(gfilepath, "%s/tmp.gz", outfolder);
  
	for (boot = 0; boot < strap; boot++)
  {
    	init_bootstrap();
    	init_tree();
      //fprintf(stderr, "py_main =========== after init_tree() ============= \n");
   		optimize_tree(imax);
    	//printf(stderr, "py_main =========== after optimize_tree(imax) ============= \n");
      free_tree(tree);
  }
  
  //free_mem();
  

  // Remove temp-file after the run.
  if (remove(gfilepath) != 0)
  	return PyLong_FromLong(-1);
  
  return PyLong_FromLong(0);	
}



// Method definition for this extension
static PyMethodDef binarysankoff_methods[] = {
  {"py_main", method_binsankoff, METH_VARARGS, "execute the RHM algorithm"},
  {NULL, NULL, 0, NULL}   /* Sentinel */
  /* https://stackoverflow.com/questions/30359255/python-sentinel-in-c-extension
     https://stackoverflow.com/questions/43371780/why-does-pymethoddef-arrays-require-a-sentinel-element-containing-multiple-nulls   */
};

// Module definition
// The arguments of this structure tell Python the name of the extension-module,
// what it's methods are and where to look for it's method definitions
static struct PyModuleDef binarysankoff =
{
    PyModuleDef_HEAD_INIT,
    "binarysankoff", /* name of module */
    "a Python module that calculates RHM algorithm from C code extension.", /* module documentation, may be NULL */
    -1,   /* size of per-interpreter state of the module, or -1 if the module keeps state in global variables. */
    binarysankoff_methods
};

//static PyObject *binarysankoffError;

// Module initialization function:
// Python calls this function when importing the extension. It is important
// that this function is named PyInit_<your_module_name> exactly, and matches
// the name keyword argument in setup.py's setup() call.
PyMODINIT_FUNC PyInit_binarysankoff(void)
{
    /*
    PyObject *m;

    m = PyModule_Create(&binarysankoff);
    if (m == NULL)
        return NULL;
    
    binarysankoffError = PyErr_NewException("binarysankoff.error", NULL, NULL);
    Py_XINCREF(binarysankoffError);
    if (PyModule_AddObject(m, "error", binarysankoffError) < 0) {
        Py_XDECREF(binarysankoffError);
        Py_CLEAR(binarysankoffError);
        Py_DECREF(m);
        return NULL;
    }
     
    return m;
    */
    
    return PyModule_Create(&binarysankoff);
}
