#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "kdtree.h"

#define VERSION "0.1"

#define MAX(a, b) ((a) > (b) ? (a) : (b))

struct {
    int depth;
} stats;

static int (*sort_functions[2])(const void *, const void *);

/* returns 2^a, where ^ is power, not XOR */
static int _pow2(int a)
{
    int i, ret = 2;

    if (a == 0)
        return 1;

    for (i = 1; i < a; i++)
        ret *= 2;
    return ret;
}

/* Should never be called directly. Only called by _compare() */
static int _x_compare(const void *a1, const void *b1)
{
    const struct node **a = (const struct node **)a1;
    const struct node **b = (const struct node **)b1;

//    printf("x comp: a lon: %.15f b lon: %.15f\n", a[0]->longitude, b[0]->longitude);

    if (a[0]->longitude < b[0]->longitude)
        return -1;
    if (a[0]->longitude > b[0]->longitude)
        return 1;
    return 0;
}

/* Should never be called directly. Only called by _compare() */
static int _y_compare(const void *a1, const void *b1)
{
    const struct node **a = (const struct node **)a1;
    const struct node **b = (const struct node **)b1;

//    printf("y comp: a lat: %.15f b lat: %.15f\n", a[0]->latitude, b[0]->latitude);

    if (a[0]->latitude < b[0]->latitude)
        return -1;
    if (a[0]->latitude > b[0]->latitude)
        return 1;
    return 0;
}


/* Should never be called directly. Only called by construct() and itself */
static int _construct(struct node **new_nodes, size_t n, int depth, struct node **treenodes, int treenodenr)
{
    int median, tmp;
    int leftdepth, rightdepth;

    if (!n)
        return depth - 1;

    qsort(new_nodes, n, sizeof(struct node *), sort_functions[depth % 2]);
    median = n >> 1;
    treenodes[treenodenr] = *(new_nodes + median);

    tmp = ((char *)(&new_nodes[median]) - (char *)new_nodes) / sizeof(struct node **);
    leftdepth = _construct(new_nodes, tmp, depth + 1, treenodes, (treenodenr << 1) + 1);

    tmp = ((char *)(&new_nodes[n]) - (char *)(&new_nodes[median + 1])) / sizeof(struct node **);
    rightdepth = _construct(new_nodes + median + 1, tmp, depth + 1, treenodes, (treenodenr << 1) + 2);

    return MAX(leftdepth, rightdepth);
}

struct node **kdtree_construct(struct node *new_nodes, unsigned int *n)
{
    struct node **sortedlist, **treearray;
    int median, i, tmp;
    int leftdepth, rightdepth;
    unsigned int treesize;

    sortedlist = malloc(*n * sizeof(struct node *));
    treesize = _pow2((int)log2((double)*n) + 1) - 1;
    treearray = malloc(treesize * sizeof(struct node *));

    sort_functions[0] = _x_compare;
    sort_functions[1] = _y_compare;

    for (i = 0; i < *n; ++i)
        *(sortedlist + i) = new_nodes + i;

    qsort(sortedlist, *n, sizeof(struct node *), _x_compare);
    median = *n >> 1;
    treearray[0] = *(sortedlist + median);

    tmp = ((char *)(&sortedlist[median]) - (char *)sortedlist) / sizeof(struct node **);
    leftdepth = _construct(sortedlist, tmp, 1, treearray, 1);

    tmp = ((char *)(&sortedlist[*n]) - (char *)(&sortedlist[median + 1])) / sizeof(struct node **);
    rightdepth = _construct(sortedlist + median + 1, tmp, 1, treearray, 2);

    stats.depth = MAX(leftdepth, rightdepth);
    free(sortedlist);
    *n = treesize;

    return treearray;
}
