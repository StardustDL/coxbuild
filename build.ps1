cd ./src/main
try {
    python -m coxbuild -D ../.. $args
}
finally {
    cd ../..
}