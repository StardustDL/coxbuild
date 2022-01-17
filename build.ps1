cd ./src
try {
    python -m coxbuild -D .. $args
}
finally {
    cd ..
}