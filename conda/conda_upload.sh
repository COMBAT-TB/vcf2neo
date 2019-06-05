set -e
# Only need to change these two variables
PKG_NAME=vcf2neo
USER=thoba
OS=$TRAVIS_OS_NAME-64

conda config --set anaconda_upload no
export CONDA_BLD_PATH=$HOME/miniconda/conda-bld
conda build .
anaconda -t $CONDA_UPLOAD_TOKEN upload -u $USER $CONDA_BLD_PATH/$OS/$PKG_NAME-*.tar.bz2 --force
