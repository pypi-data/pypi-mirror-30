
#include <errno.h>
#include "pastml.h"


int output_ancestral_states(Tree *tree, size_t num_annotations, char **character, char *output_file_path) {
    FILE* outfile = fopen(output_file_path, "w");
    if (!outfile) {
        fprintf(stderr, "Output annotation file %s is impossible to access.", output_file_path);
        fprintf(stderr, "Value of errno: %d\n", errno);
        fprintf(stderr, "Error opening the file: %s\n", strerror(errno));
        return ENOENT;
    }
    size_t i, j, k;
    Node* nd;

    // print the header
    fprintf(outfile, "node ID");
    for (i = 0; i < num_annotations; i++) {
        fprintf(outfile, ",%s", character[i]);
    }
    fprintf(outfile, "\n");


    for (k = 0; k < tree->nb_nodes; k++) {
        nd = tree->nodes[k];

        fprintf(outfile, "%s", nd->name);

        for (i = 0; i < num_annotations; i++) {
            for (j = 0; j < num_annotations; j++) {
                if (strcmp(character[i], character[nd->best_states[j]]) == 0) {
                    fprintf(outfile, ",%.8f", nd->result_probs[j]);
                }
            }
        }
        fprintf(outfile, "\n");
    }

    fclose(outfile);
    return EXIT_SUCCESS;
}
