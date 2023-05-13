!# /bin/bash

echo "Build the images for the project"
for d in orion_* ; do
    echo "Building $d"
    cd $d
    docker build -t cocerxkubecr.azurecr.io/$d .
    docker push cocerxkubecr.azurecr.io/$d
    cd ..
done
