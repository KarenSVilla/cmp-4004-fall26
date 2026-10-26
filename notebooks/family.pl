
parent(tom, bob).
parent(bob, ann).
parent(bob, pat).
male(tom).
male(bob).
female(ann).
female(pat).

father(X, Y) :- parent(X, Y), male(X).
grandparent(X, Z) :- parent(X, Y), parent(Y, Z).

ancestor(X, Y) :- parent(X, Y).
ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y).

% The animal taxonomy from deck 05 slide 7 -- otherwise orphaned content.
isa(bluebird, bird).
isa(bird, vertebrate).
hascovering(bird, feathers).
hasproperty(bird, flies).
hassize(bluebird, small).

% Inheritance in ONE line. This is what propositional logic could not express.
inherits(X, P) :- hasproperty(X, P).
inherits(X, P) :- isa(X, Y), inherits(Y, P).
