### This folder contains a project that was evaluated as part of the _Electromagnetism and Optics laboratory_ course, during the $2^{nd}$ year of the _Physics_ Bachelor's programme in Bologna.  
### The goal was to simulate the decaying processes of different particles, like the ones that occur during high energy experiments at particle accelerators, using _C++_ scripts to create the simulation and _ROOT_ for analysis and visualisation.

## Tasks:
1) Create $10^5$ events of 100 particles each, with the particle types following this distribution:
   * $\pi^+$: 40%
   * $\pi^-$: 40%
   * $K^+$: 5%
   * $K^-$: 5%
   * $p^+$: 4.5%
   * $p^-$: 4.5%
   * $K^*$: 1%
    
2) Assign to each particle the following properties, each one following its own PDF:
   * _Azimutal Angle_
   * _Polar Angle_
   * _Total Momentum_

3) Plot the distributions for the particle properties, including the particle types

4) Plot the invariant mass distributions for the following combinations:
   * Particles decayed from the same K*
   * Difference between combinations of same and opposite charges (counting only Pions and Kaons)
   * Difference between combinations of same and opposite charges (counting all particles)

## Content:
- _**Particle.hpp**_ and _**Particle.cpp**_: here the _Particle_ class and all of its methods, i.e. the constructors, _getters_, index setters (to assign a type to a particle), along with the methods needed to boost the particles and make them decay, are defined
- _**ParticleType.hpp**_ and _**ParticleType.cpp**_: here the _ParticleType_ class and its _getters_ are defined
- _**ResonanceType.hpp**_ and _**ResonanceType.cpp**_: here the _ResonanceType_ class and its methods (_GetWidth() and Print()_) are defined
- _**main.cpp**_: here the full simulation is implemented, creating all the particles, assigning them the required parameters, computing the various invariant mass combinations and creating the plots
- _**outputs/**_: here are stored the _.jpg_ and _.root_ files for both the **particle properties** and **invariant masses** distributions
