#ifndef __KDTREE_H /* start of include guard */
#define __KDTREE_H

struct __attribute__((packed)) node {
    double longitude;
    double latitude;
    unsigned char speed;
};

extern struct node **kdtree_construct(struct node *new_nodes, unsigned int *n);
extern struct node **kdtree_get_nodes_in_array(struct node *root, int *numnodes);

#endif /* end of include guard: __KDTREE_H */
