/**
    Matrix fitting functions translated into C
    from the original Fortran implementation
    with help from f2c.
*/
#include <math.h>

#define EPS 1e-12
#define PI 3.14159265358979f
#define ONETHIRD 0.333333333f
#define FOURTHIRDS 1.333333333f

typedef int bool;

/* Builtin Functions */
double atan(double);
double cos(double);
double fabs(double);
double sqrt(double);

/* Function Declarations */
int matfit(const long n, const float *xa, const float *xb,
            float *r, float *v, float *rmse,
            const bool entry);

int matfitw(const long n, const float *xa, const float *xb,
            float *r, float *v, float *rmse,
            const bool entry, const float *w);

int qkfit(double *umat, double *rtsum, float *r, const bool entry);

int eigen(double *a, double *r, const long n, const bool mv);

int esort(double *a, double *r, const long n, const bool mv);


/**
    Function to fit the coord set xa(3,n) to the set xb(3,n)
    in the sense of:
            xa = r * xb + v
    r is a unitary 3.3 right handed rotation matrix
    and v is the offset vector. This is an exact solution.

    If entry is logically false only the rms coordinate error
    will be returned (but quickly)

    This function is a combination of McLachlan's and Kabsch's
    techniques. See
    Kabsch, W. ACTA CRYST A34, 827,1978
    McLachan, A.D., J. MOL. BIO. NNN, NNNN 1978
    Written by S.J. Remington 11/78.

    This function uses the IBM SSP eigenvalue routine 'eigen'
*/
int matfit(const long n, const float *xa, const float *xb,
            float *r, float *v, float *rmse,
            const bool entry)
{
    long i, j, k;
    double t, xn, rtsum, xni, xasq, xbsq;
    double cma[3], cmb[3], umat[9];

    xn = (double) n;
    xasq = 0.0f;
    xbsq = 0.0f;
    xni = 1.0f / xn;

    // Accumulate uncorrected (for C.M.) sums and squares
    for (i = 0; i < 3; ++i) {
	    cma[i] = 0.0f;
	    cmb[i] = 0.0f;

	    for (j = 0; j < 3; ++j) {
	        umat[i + j * 3] = 0.0f;
	    }

	    for (j = 0; j < n; ++j) {
	        for (k = 0; k < 3; ++k) {
		        umat[i + k * 3] += xa[i + j * 3] * xb[k + j * 3];
            }

            t = xa[i + j * 3];
            cma[i] += t;
            xasq += t * t;

            t = xb[i + j * 3];
            cmb[i] += t;
            xbsq += t * t;
	    }
    }

    // Subtract CM offsets
    for (i = 0; i < 3; ++i) {
        xasq -= cma[i] * cma[i] * xni;
        xbsq -= cmb[i] * cmb[i] * xni;

        for (j = 0; j < 3; ++j) {
            umat[i + j * 3] = (umat[i + j * 3] - cma[i] * cmb[j] * xni) * xni;
        }
    }

    // Fit it
    qkfit(umat, &rtsum, r, entry);
    *rmse = (xasq + xbsq) * xni - rtsum * 2.0f;

    if (*rmse < 0.0f) {
	    *rmse = 0.0f;
    }
    *rmse = sqrt(*rmse);

    // Calculate offset if entry is true
    if (entry) {
        for (i = 0; i < 3; ++i) {
            t = 0.0f;

            for (j = 0; j < 3; ++j) {
                t += r[i + j * 3] * cmb[j];
            }
            v[i] = (cma[i] - t) * xni;
        }
    }

    return 0;
}



/**
    Function to fit the coord set xa(3,n) to the set xb(3,n)
    in the sense of:
            xa = r * xb + v
    r is a unitary 3.3 right handed rotation matrix
    and v is the offset vector. This is an exact solution.

    If entry is logically false only the rms coordinate error
    will be returned (but quickly)

    This function is a combination of McLachlan's and Kabsch's
    techniques. See
    Kabsch, W. ACTA CRYST A34, 827,1978
    McLachan, A.D., J. MOL. BIO. NNN, NNNN 1978
    Written by S.J. Remington 11/78.

    This function uses the IBM SSP eigenvalue routine 'eigen'
*/
int matfitw(const long n, const float *xa, const float *xb,
            float *r, float *v, float *rmse,
            const bool entry, const float *w)
{
    long i, j, k;
    double t, xn, rtsum, xni, xasq, xbsq;
    double cma[3], cmb[3], umat[9];

    xn = 0.0f;
    for (i = 0; i < n; ++i) {
	    xn += w[i];
    }
    xasq = 0.0f;
    xbsq = 0.0f;
    xni = 1.0f / xn;

    // Accumulate uncorrected (for C.M.) sums and squares
    for (i = 0; i < 3; ++i) {
        cma[i] = 0.0f;
        cmb[i] = 0.0f;

        for (j = 0; j < 3; ++j) {
            umat[i + j * 3] = 0.0f;
	    }

        for (j = 0; j < n; ++j) {

            for (k = 0; k < 3; ++k) {
                umat[i + k * 3] += xa[i + j * 3] * xb[k + j * 3] * w[j];
            }

            t = xa[i + j * 3];
            cma[i] += t * w[j];
            xasq += t * t * w[j];

            t = xb[i + j * 3];
            cmb[i] += t * w[j];
            xbsq += t * t * w[j];
	    }
    }

    // Subtract CM offsets
    for (i = 0; i < 3; ++i) {
        xasq -= cma[i] * cma[i] * xni;
        xbsq -= cmb[i] * cmb[i] * xni;

        for (j = 0; j < 3; ++j) {
            umat[i + j * 3] = (umat[i + j * 3] - cma[i] * cmb[j] * xni) * xni;
        }
    }

    // Fit it
    qkfit(umat, &rtsum, r, entry);

    *rmse = (xasq + xbsq) * xni - rtsum * 2.0f;

    if (*rmse < 0.0f) {
	    *rmse = 0.0f;
    }
    *rmse = sqrt(*rmse);

    // Calculate offset if entry is true
    if (entry) {
        for (i = 0; i < 3; ++i) {
            t = 0.0f;

            for (j = 0; j < 3; ++j) {
                t += r[i + j * 3] * cmb[j];
            }
            v[i] = (cma[i] - t) * xni;
        }
    }
    return 0;
}



int qkfit(double *umat, double *rtsum, float *r, const bool entry)
{
    int isig;
    long i, j, k, ia;
    double s, t, rt, digav, diff;
    double b1, b2, b13, b23, b33;
    double cc, dd, qq, du11, du21, du31, detu;
    double theta, argsq, cos3th;
    double root[3];

    double a[9];
    double *usqmat = &a[0];
    double *aam = &a[0];
    double *bam = &a[4];
    double *cam = &a[8];
    double *fam = &a[7];
    double *gam = &a[6];
    double *ham = &a[3];

    double b[9];
    double *utr = &b[0];

    // The 'eigenvalue only' entry was adapted from program by A.D. McLachan 7/78
    isig = 1;

    if (entry) {
        // If entry is true get out the rotation matrix

        // This is the fancy part
        // Form usq = (ut) . u    (in upper triangular symmetric storage mode)
        for (i = 0; i < 3; ++i) {
            for (j = i; j < 3; ++j) {
                t = 0.0f;
                for (k = 0; k < 3; ++k) {
                    t += umat[k + i * 3] * umat[k + j * 3];
                }
                ia = i + (j * j + j) / 2;
                utr[ia] = t;
            }
        }

        // Calculate eigenvalues and vectors
        eigen(utr, a, 3, 0);
        esort(utr, a, 3, 0);

        root[0] = utr[0];
        root[1] = utr[2];
        root[2] = utr[5];

        // Set a3 = a1 cross a2
        // Roots are in order r[0] >= r[1] >= r[2] >= 0

        a[6] = a[1] * a[5] - a[2] * a[4];
        a[7] = a[2] * a[3] - a[0] * a[5];
        a[8] = a[0] * a[4] - a[1] * a[3];

        // Vector set b = u . a
        for (i = 0; i < 3; ++i) {
            for (j = 0; j < 3; ++j) {
                t = 0.0f;
                for (k = 0; k < 3; ++k) {
                    t += umat[j + k * 3] * a[k + i * 3];
                }
                b[j + i * 3] = t;
            }
        }

        // Normalize b1 and b2 and calculate b3 = b1 cross b2
        b1 = sqrt(b[0] * b[0] + b[1] * b[1] + b[2] * b[2]);
        b2 = sqrt(b[3] * b[3] + b[4] * b[4] + b[5] * b[5]);
        for (i = 0; i < 3; ++i) {
            b[i] /= b1;
            b[i + 3] /= b2;
        }

        // Check for left handed rotation
        b13 = b[1] * b[5] - b[2] * b[4];
        b23 = b[2] * b[3] - b[0] * b[5];
        b33 = b[0] * b[4] - b[1] * b[3];

        s = b13 * b[6] + b23 * b[7] + b33 * b[8];
        if (s < 0.0f) {
            isig = -1;
        }
        b[6] = b13;
        b[7] = b23;
        b[8] = b33;

        // Calculate rotation matrix r
        for (i = 0; i < 3; ++i) {
            for (j = 0; j < 3; ++j) {
                t = 0.0f;
                for (k = 0; k < 3; ++k) {
                    t += b[i + k * 3] * a[j + k * 3];
                }
                r[i + j * 3] = t;
            }
        }

        // RMS error
        for (i = 0; i < 3; ++i) {
            if (root[i] < 0.0f) {
                root[i] = 0.0f;
            }
            root[i] = sqrt(root[i]);
        }

    } else {
        // entry is false: no rotation matrix

        // Calc det of umat
        du11 = umat[4] * umat[8] - umat[7] * umat[5];
        du21 = umat[7] * umat[2] - umat[1] * umat[8];
        du31 = umat[1] * umat[5] - umat[4] * umat[2];
        detu = umat[0] * du11 + umat[3] * du21 + umat[6] * du31;

        if (detu < 0.0f) {
            isig = -1;
        }

        // Form usqmat as positive semi definite matrix
        for (j = 0; j < 3; ++j) {
            for (i = 0; i <= j; ++i) {
                usqmat[i + j * 3] = umat[i * 3] * umat[j * 3] +
                                    umat[i * 3 + 1] * umat[j * 3 + 1] +
                                    umat[i * 3 + 2] * umat[j * 3 + 2];
            }
        }

        // Reduce avg of diagonal terms to zero
        digav = (*aam + *bam + *cam) * ONETHIRD;
        *aam -= digav;
        *bam -= digav;
        *cam -= digav;

        // Setup coeffs of secular equation of matrix with trace zero
        cc = (*fam * *fam) + (*gam * *gam) + (*ham * *ham) -
             (*aam * *bam) - (*bam * *cam) - (*cam * *aam);

        dd = (*aam * *bam * *cam) + 2.0 * (*fam * *gam * *ham) -
             (*aam * *fam * *fam) - (*bam * *gam * *gam) - (*cam * *ham * *ham);

        // The secular eqn is y^3 - cc * y - dd = 0 and dd is det(usqmat)
        // Reduce this to the form cos^3 - (3/4)cos - (1/4)cos3theta = 0
        // with solutions costheta. So y = qq * costheta
        if (cc <= EPS) {
            // Special for triply degenerate
            root[0] = 0.0f;
            root[1] = 0.0f;
            root[2] = 0.0f;

        } else {

            qq = sqrt(FOURTHIRDS * cc);
            cos3th = 3.0 * dd / (cc * qq);

            if (fabs(cos3th) > 1.0) {
                cos3th = (cos3th >= 0) ? 1.0 : -1.0;
            }

            // Function arcos
            if (cos3th != 0.0f) {
                argsq = cos3th * cos3th;
                theta = atan(sqrt(1.0f - argsq) / cos3th);

                if (cos3th < 0.0f) {
                    theta = PI - theta;
                }
            } else {
                theta = 1.570796327f;
            }

            // Roots in order of size go GO 1,2,3 1 largest
            theta *= ONETHIRD;
            root[0] = qq * cos(theta);
            diff = 0.5 * sqrt(3.0 * (qq * qq - root[0] * root[0]));
            root[1] = -root[0] * 0.5 + diff;
            root[2] = -root[0] * 0.5 - diff;
        }

        // Add on digav and take sqrt
        for (i = 0; i < 3; ++i) {
            rt = root[i] + digav;
            if (rt < EPS) {
                rt = 0.0f;
            }
            root[i] = sqrt(rt);
        }
    }

    // Change sign of eval #3 if left handed
    if (isig == -1) {
        root[2] = -root[2];
    }
    *rtsum = root[0] + root[1] + root[2];

    return 0;
}



/**
    Subroutine to compute eigenvalues & eigenvectors of a real symmetric
    matrix, stolen from IBM SSP manual (See p165)
    Description of parameters:

    a - Original matrix stored columnwise as upper triangle only,
    Eigenvalues are written into diagonal
    elements of a i.e. a(0) a(4) a(8) for a 3*3 matrix.

    r - Resultant matrix of eigenvectors stored columnwise in same order as eigenvalues

    n - Order of matrices a & r

    mv = 0 to compute eigenvalues & eigenvectors.
*/
int eigen(double *a, double *r, const long n, const bool mv)
{
    long i, j, l, m;
    long ia, ij, il, im, iq, ll, lm, lq, mm, mq, ilq, imq, ilr, imr, ind;
    double x, y;
    double sinx, sinx2, cosx, cosx2, sincs;
    double thr, anorm, anrmx;

    if (mv == 0) {
        iq = -n;
        for (j = 0; j < n; ++j) {
            iq += n;
            for (i = 0; i < n; ++i) {
                ij = iq + i;
                if (i == j) {
                    r[ij] = 1.0f;
                } else {
                    r[ij] = 0.0f;
                }
            }
        }
    }

    // Initial and final norms (anorm & anrmx)
    anorm = 0.0f;
    for (i = 1; i <= n; ++i) {
        for (j = i; j <= n; ++j) {
            if (i != j) {
                ia = i + (j * j - j) / 2 - 1;
                anorm += a[ia] * a[ia];
            }
	    }
    }

    if (anorm <= 0.0) {
        return 0;
    }

    anorm = sqrt(anorm * 2.0f);
    anrmx = anorm * EPS / n;

    // Compute threshold
    thr = anorm;

    do {
        thr /= n;
        do {
            // Initialize indicator
            ind = 0;
            for (l = 1; l <= (n-1); ++l) {
                for (m = l + 1; m <= n; ++m) {
                    // Compute sin & cos
                    mq = (m * m - m) / 2;
                    lq = (l * l - l) / 2;
                    lm = l + mq - 1;

                    if (fabs(a[lm]) >= thr) {
                        ind = 1;
                        ll = l + lq - 1;
                        mm = m + mq - 1;
                        x = (a[ll] - a[mm]) * 0.5;

                        y = -(a[lm]) / sqrt(a[lm] * a[lm] + x * x);

                        if (x < 0.0) {
                            y = -y;
                        }

                        sinx = y / sqrt((sqrt(1.0f - y * y) + 1.0f) * 2.0f);
                        sinx2 = sinx * sinx;

                        cosx = sqrt(1.0f - sinx2);
                        cosx2 = cosx * cosx;

                        sincs = sinx * cosx;

                        // Rotate L & M columns
                        ilq = n * (l - 1);
                        imq = n * (m - 1);
                        for (i = 1; i <= n; ++i) {
                            iq = (i * i - i) / 2;

                            if ((i != l) && (i != m)) {
                                if (i < m) {
                                    im = i + mq - 1;
                                } else {
                                    im = m + iq - 1;
                                }

                                if (i < l) {
                                    il = i + lq - 1;
                                } else {
                                    il = l + iq - 1;
                                }

                                x = a[il] * cosx - a[im] * sinx;
                                a[im] = a[il] * sinx + a[im] * cosx;
                                a[il] = x;
                            }

                            if (mv == 0) {
                                ilr = ilq + i - 1;
                                imr = imq + i - 1;
                                x = r[ilr] * cosx - r[imr] * sinx;
                                r[imr] = r[ilr] * sinx + r[imr] * cosx;
                                r[ilr] = x;
                            }
                        }

                        x = a[lm] * 2.0f * sincs;
                        y = a[ll] * cosx2 + a[mm] * sinx2 - x;
                        x = a[ll] * sinx2 + a[mm] * cosx2 + x;
                        a[lm] = (a[ll] - a[mm]) * sincs + a[lm] * (cosx2 - sinx2);
                        a[ll] = y;
                        a[mm] = x;
                    }
                } // Loop until m = last column
            } // Loop until l = penultimate column
        } while (ind == 1); // Loop until indicator is false
    } while ((thr - anrmx) > 0.0); // Completion: compare threshold with final norm

    return 0;
}



/**
    Function to sort eigenvalues and eigenvectors
    in descending order of eigenvalues
*/
int esort(double *a, double *r, const long n, const bool mv)
{
    long i, j, k;
    long ll, iq, jq, mm, ilr, imr;
    double x;

    iq = -n;
    for (i = 1; i <= n; ++i) {
        iq += n;
        ll = i + (i * i - i) / 2 - 1;
        jq = n * (i - 2);

        for (j = i; j <= n; ++j) {
            jq += n;
            mm = j + (j * j - j) / 2 - 1;
            if (a[ll] - a[mm] < 0.0) {
                x = a[ll];
                a[ll] = a[mm];
                a[mm] = x;

                if (mv == 0) {
                    for (k = 1; k <= n; ++k) {
                        ilr = iq + k - 1;
                        imr = jq + k - 1;

                        x = r[ilr];
                        r[ilr] = r[imr];
                        r[imr] = x;
                    }
                }
            }
	    }
    }
    return 0;
}
