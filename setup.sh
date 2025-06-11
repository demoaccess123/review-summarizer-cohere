#!/bin/bash

mkdir -p ~/.streamlit/

echo "
[server]
headless = true
port = $PORT
enableCORS = false
<<<<<<< HEAD
" > ~/.streamlit/config.toml
=======
" > ~/.streamlit/config.toml

>>>>>>> 6669c563fa3426cfed51afe24494201dc1bbeac9
