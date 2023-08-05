#include <math.h>

/* Builtin Functions */
double floor(double);

/* Function Declarations */
int fit_frame(const long n_atoms, const float *in_frame,
                const float *r, const float *v, float *out_frame);

int fast_pib(const long n_atoms, const float *in_coords,
                const float *box, float *out_coords);



/**
    Applies the rotation matrix r and offset vector v
    to transforms in_frame coordinates into out_frame
*/
int fit_frame(const long n_atoms, const float *in_frame,
                 const float *r, const float *v, float *out_frame)
{
    int j, k;
    long i;

    for (i = 0; i < n_atoms; ++i) {
        for (j = 0; j < 3; ++j) {

            out_frame[i * 3 + j] += v[j];

            for (k = 0; k < 3; ++k) {
                out_frame[i * 3 + j] += r[k * 3 + j] * in_frame[i * 3 + k];
            }
        }
    }
    return 0;
}



/**
    Wraps coordinates from in_coords into primary unit
    cell box, and returns output in out_coords
*/
int fast_pib(const long n_atoms, const float *in_coords,
                const float *box, float *out_coords)
{
    long i, i0, i1, i2;
    float s, boxinv[3];

    boxinv[0] = 1.0f / box[0];
    boxinv[1] = 1.0f / box[4];
    boxinv[2] = 1.0f / box[8];

    for (i = 0; i < n_atoms; ++i)
    {
        i0 = i * 3;
        i1 = i0 + 1;
        i2 = i0 + 2;

        s = floor(in_coords[i2] * boxinv[2]);
        out_coords[i2] = in_coords[i2] - s * box[8];
        out_coords[i1] = in_coords[i1] - s * box[7];
        out_coords[i0] = in_coords[i0] - s * box[6];

        s = floor(in_coords[i1] * boxinv[1]);
        out_coords[i1] -= s * box[4];
        out_coords[i0] -= s * box[3];

        s = floor(in_coords[i0] * boxinv[0]);
        out_coords[i0] -= s * box[0];
    }
    return 0;
}
