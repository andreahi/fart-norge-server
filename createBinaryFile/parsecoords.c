/* gcc -lm -O2 kdtree.c parsecoords.c -o parsecoords */

#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include "kdtree.h"

#define VERSION "0.1"

struct files {
    int fd;
    unsigned int nodes;
};

/* returns the big endian representation of a */
static inline int big_endian32(int a)
{
#if __GNUC__ <= 4 && __GNUC_MINOR__ < 2
    register int ret;
    asm("bswap  %%eax" :"=a"(ret) :"a"(a));
    return ret;
#else
    return __builtin_bswap32(a);
#endif
}

/* write the kdtree to a file. */
void tree_to_fd(int fd, struct node **treenodes, unsigned int num_nodes)
{
    int i, j, writecount;
    int emptycoord = big_endian32(100000000);
    unsigned char emptyspeed = 255;
    /* temporary structure used for nodes */
    struct __attribute__((packed)) lol {
        int a, b;
        unsigned char c;
    } *bufferptr, *buffer;
    /* allocate a buffer for the nodes. we write 1024 nodes at the time to
     * reduce runtime */
    buffer = malloc(1024 * sizeof(struct lol));

    i = 0;
    while (i < num_nodes) {
        /* fill the buffer with <= 1024 nodes */
        bufferptr = buffer;
        for (j = 0; j < 1024 && i < num_nodes; ++j, ++i, ++bufferptr) {
            /* use a specified number for empty nodes */
            if (treenodes[i] == NULL) {
                bufferptr->a = bufferptr->b = emptycoord;
                bufferptr->c = emptyspeed;

                //                printf("%d - lat: %22d lon: %22d\r\n", i, bufferptr->a, bufferptr->b);

            } else {

                /* convert coordinates to big endian integers */
                bufferptr->a = (int)(treenodes[i]->longitude * 1000000);
                bufferptr->b = (int)(treenodes[i]->latitude * 1000000);
                bufferptr->c = treenodes[i]->speed;

                if (j >= 0 && j <= 10) {
//                    printf("%d - lat: %.15f lon: %.15f\r\n", i, treenodes[i]->latitude, treenodes[i]->longitude);
//                    printf("%d - lat: %d lon: %d\r\n", i, bufferptr->b, bufferptr->a);
                }

                bufferptr->b = big_endian32(bufferptr->b);
                bufferptr->a = big_endian32(bufferptr->a);
            }
        }
        /* do the write */
        writecount = 0;
        int tmp_write_count = 0;
        while (writecount < j * sizeof(struct lol)) {
            tmp_write_count = write(fd, (char *)buffer + writecount, (j - writecount) * sizeof(struct lol));
            writecount += tmp_write_count > 0 ? tmp_write_count : 0;
        }
    }
    free(buffer);
}

/* Opens the files for all fylker supplied in argv.
 * Return number of files opened */
int open_files(struct files *fds, unsigned int *totalnumnodes, char **argv)
{
    int i;
    char buffer[64];

    /* will contain the total number of nodes in all the files */
    *totalnumnodes = 0;

    for (i = 0; argv[i] != NULL; i++) {
        // fylke 13 finnes ikke
        if (i == 13)
            continue;

        /* open the file */
        sprintf(buffer, "./fylkedata/fylke_%s.bin", argv[i]);
        if ((fds[i].fd = open(buffer, O_RDONLY)) == -1) {
            fprintf(stderr, "Fant ingen fil for fylke %d\n", i);
            continue;
        }

        /* read number of nodes. (last 4 bytes of the file) */
        lseek(fds[i].fd, -4, SEEK_END);
        read(fds[i].fd, &fds[i].nodes, 4);
        lseek(fds[i].fd, SEEK_SET, 0);
        *totalnumnodes += fds[i].nodes;
    }

    return i;
}

int main(int argc, char *argv[])
{
    int i, j, numfiles, tmp;
    unsigned int totalnumnodes;
    struct files fds[22];
    struct node *nodes, **treenodes;
    int outfd;

    if (argc < 2) {
        fprintf(stderr, "USAGE: %s <option> <file|filedescriptor> fylker ...\n", argv[0]);
        fprintf(stderr, "Options are the following:\n");
        fprintf(stderr, "   -f  - write output to a file. The next argument in argv, "
                "must be the filename\n");
        fprintf(stderr, "   -d  - write output to a file descriptor. The next argument "
                "in argv, must be an open file descriptor\n");
        return -1;
    }

    /* write output to a file */
    if (argv[1][0] == '-' && argv[1][1] == 'f') {
        if ((outfd = open(argv[2], O_WRONLY|O_CREAT, (mode_t)(0600))) == -1) {
            perror("open");
            return 1;
        }
    } else /* write output to a supplied filedescriptor */
        outfd = atoi(argv[2]);

    numfiles = open_files(fds, &totalnumnodes, argv + 3);
    nodes = malloc(totalnumnodes * sizeof(struct node));
    for (i = tmp = 0; i < numfiles; ++i) {
        j = fds[i].nodes * sizeof(struct node);
        read(fds[i].fd, nodes + tmp, j);
        tmp += fds[i].nodes;

        close(fds[i].fd);
    }

    treenodes = kdtree_construct(nodes, &totalnumnodes);

    /* if a file descriptor is supplied, write the data size to it */
    if (argv[1][1] == 'd') {
        i = ((totalnumnodes * 2) * sizeof(int)) + totalnumnodes;
        write(outfd, &i, sizeof(int));
    }

    tree_to_fd(outfd, treenodes, totalnumnodes);
    close(outfd);

    return 0;
}
