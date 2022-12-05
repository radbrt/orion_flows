!# /bin/bash
echo "Build the images for the project"
for d in orion_* ; do
    echo "Building $d"
    cd $d
    docker build -t radbrt/$d .
    docker push radbrt/$d
    cd ..
done
