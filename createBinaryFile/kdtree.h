#ifndef __KDTREE_H /* start of include guard */
#define __KDTREE_H

// I stole these
#define likely(x) __builtin_expect(!!(x), 1)
#define unlikely(x) __builtin_expect(!!(x), 0)

struct __attribute__((packed)) node {
    double longitude;
    double latitude;
    unsigned int speed :4;
    unsigned int atk_strekning :1;
    unsigned int reserved :27;
};

struct __attribute__((packed)) outnode {
    int lo, la;
    unsigned int speed :4;
    unsigned int atk_strekning :1;
    unsigned int reserved :27;
};

extern struct node **kdtree_construct(struct node *new_nodes, unsigned int *n);
extern struct node **kdtree_get_nodes_in_array(struct node *root, int *numnodes);

#endif /* end of include guard: __KDTREE_H */
