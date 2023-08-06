# gridworld
An implementation of a gridworld environment based off of the arcade python library

## Installation via a Conda Environment
In the root directory of this project:

    conda env create -f environment.yml
    source gridworld
    pip install -e .

## Usage

    python gridworld/main.py
    
### Controls
* space - pause/resume
* enter - reset
* left/right - increase/decrease speed of animation
    
## Requirements (handled by conda environment installation method)
* Python3.6
* arcade
