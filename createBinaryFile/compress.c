#include <sys/stat.h>
#include <archive.h>
#include <archive_entry.h>
#include <fcntl.h>
#include <stdlib.h>
#include <unistd.h>

#include "kdtree.h"

static int myopen(struct archive *a, void *client_data)
{
    return ARCHIVE_OK;
}

static ssize_t mywrite(struct archive *a, void *fd, const void *buff, size_t n)
{
    return write((int)fd, buff, n);
}

static int myclose(struct archive *a, void *client_data)
{
    return 0;
}

void write_compressed(int outfd, struct node **array, int num_nodes, char *filename)
{
    int fd, len, i;
    struct stat st;
    char buff[8192];
    struct archive *a;
    struct archive_entry *entry;

    a = archive_write_new();
    archive_write_add_filter_gzip(a);
    archive_write_set_format_ustar(a);
    archive_write_open(a, outfd, myopen, mywrite, myclose);

    entry = archive_entry_new();

    st.st_size = num_nodes * sizeof(struct node);
    archive_entry_copy_stat(entry, &st);

    archive_entry_set_pathname(entry, filename);
    archive_write_header(a, entry);

    for (i = 0; i < num_nodes; ++i)
        archive_write_data(a, array[i], sizeof(struct node));

    archive_entry_free(entry);
    archive_write_free(a);
}
