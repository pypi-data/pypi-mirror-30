echo "cleaning..."
find ./pfnet -name \*.so -delete
find ./pfnet -name \*.pyc -delete
find ./tests -name \*.pyc -delete
find ./examples -name \*.pyc -delete
find . -name libpfnet* -delete
rm -rf PFNET.egg-info
rm -f ./pfnet/cpfnet.c
rm -rf build
rm -rf dist
rm -rf lib/pfnet
