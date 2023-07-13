# Building a healthier feed: Private location trace intersection driven feed recommendations
A paper by Tobin South, Nick Lothian, Taka Yabe, and Alex 'Sandy' Pentland. Presented at the 16th International Conference on Social Computing, Behavioral-Cultural Modeling, & Prediction and Behavior Representation in Modeling and Simulation, September 2023.

## Structure
This repo has three main sections:

* A python technical demo for matching on location data or images using private set intersection, and how this could be mapped to a feed.
* The figures and reproducible results for the paper.
* A React web demo to show how this could be used in a javascript context. This is being worked to integrate directly with Verdia datastores. Minimal viable code for a website is available here. While separated [client](https://github.com/tuanldVGU/bc_profile_matcher/tree/loginVerida) and [server](https://github.com/tuanldVGU/bc_profile_matcher_APIs) repositories are available elsewhere (which now use less typescript). These are still being developed and will require you to self host.
