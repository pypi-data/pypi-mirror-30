#<Title>

##A Python package for caclulating Multivaraible Shannon Entropy and other Information Theoretic Measures

##API

The API and internals for this package are functional in nature. 
Users will call functions with data sets as arguments and the specified measures will be returned

##Implementation

The implementation of this package is done using mixed entropy. For the discrete only case this will collapse to Shannon Entropy
and for the continuous only case this will collapse to differential entropy. 
The number of variables within the continuous part and within the discrete part are not
bounded, however performance will suffer on higher dimensional data sets.
The implementation is currently pure python, using Numpy.

The continuous part of the Entropy calculation is done via Gaussian-Hermite Quadrature on a Gaussian Kernel Density Estimation of the specified data.

The API functions will take arguments to allow for the function to calculate cross entropy or conditional entropy (or conditional cross entropy). 
The defaults for many of these arguments is None.
Data arguments for the functions are of type numpy.ndarray.

##Arguments

Many of the arguments are named the same and behave the same accross the differing API functions.

disc_data - This is the discrete part of the primary data for which the entropy will be calculate.
The default value is None which is used for the case where there is no discrete data.

cont_data - This is the continuous part of the primary data for which the entropy will be calculate.
The default value is None which is used for the case where there is no continuous data.

cond_disc_data - This is the discrete part of the conditional data for which the entropy will be calculate.
The default value is None which is used for the case where there is no discrete conditional data.

cond_cont_data - This is the discrete part of the conditional data for which the entropy will be calculate.
The default value is None which is used for the case where there is no continuous conditional data.

cross_disc_data - This is the discrete part for any cross data (for cross entropy measures).
The default value is None which is used for the case where there is no discrete cross data. 
If  cross_cont_data is also None: this collapses to mixed entropy rather than mixed cross entropy.

cross_cont_data - This is the continuous part for any cross data (for cross entropy measures).
The default value is None which is used for the case where there is no continuous cross data. 
If  cross_disc_data is also None: this collapses to mixed entropy rather than mixed cross entropy.

cond_disc_data - This is the discrete part of the conditional cross data for which the entropy will be calculate.
The default value is None which is used for the case where there is no discrete cross conditional data.

cond_cont_data - This is the discrete part of the conditional cross data for which the entropy will be calculate.
The default value is None which is used for the case where there is no continuous cross conditional data.

covariance_multiplier - This is essentially the multi-dimensional bandwidth parameter used for the Kernel Density Estimation.
The default value is e**-1. For N dimensional continuous data, the covariance multiplier will be the Nth root of the input argument.
This is so that the proportional volume of the local Gaussian convolution will remain constant amongst varying dimensional data sets.

quadrature_eval_number - This is the number of evaluation points that would be used for gaussian-hermite quadrature.
For N dimensional continuous data, the number of evaluation points will be the input argument raised to the power N.
The default value is 5 thus implying for 1D data, 5 evaluation points will be take, for 2D data 25 points, 3D data 125 points and so on.

lambda_val - This is used exclusively for lambda divergence. For usage in any other measure, resort to the default value of 1.

disc_data_cont_data_tuple_list - This is used for Total_Correlation and Joint_Entropy.
Arguments should take the form "[(disc1,cont1),(disc2,cont2),...(discN-1,contN-1),(discN,contN)]"
where (discK,contK) are the discrete and continuous parts of a speicifed variable. Note that each variable may also be of any number of dimensions.

##Main User Functions

####Conditional_Entropy
This is the main function for calculating mixed entropy. It has arguments to allow for different measures.
Calculates the Mixed Entropy if no conditional or cross data is provided.
Calculates the Conditional Mixed Entropy if no cross data is provided.
Calculates the Mixed Cross Entropy if no conditional data is provided.
Calculates Conditional Mixed Cross Entropy if all arguments are provided.
Note that to calculate Joint Conditional Entropy, the data of multiple variables can be concatenated by their respective discrete and continuous parts.
Arguments:
disc_data; default = None
cont_data; default  = None
cond_disc_data; default = None
cond_cont_data; default = None
cross_disc_data; default = None
cross_cont_data; default = None
cross_cond_disc_data; default = None
cross_cond_cont_data; default = None
covariance_multiplier; default = e**-1
quadrature_eval_number; default = 5
lambda_val; default = 1

###Mutual Information
This is the main function for calculating mutual information. It has arguments to allow for different measures.
Calculates the Mixed Mutual Information if no conditional or cross data is provided.
Calculates the Conditional Mixed Mutual Information if no cross data is provided.
Calculates the Mixed Cross Mutual Information if no conditional data is provided.
Calculates Conditional Mixed Cross Mutual Information if all arguments are provided.
Arguments:
disc_data1; default = None
cont_data1; default  = None
disc_data2; default = None
cont_data2; default  = None
cond_disc_data; default = None
cond_cont_data; default = None
cross_disc_data1; default = None
cross_cont_data1; default = None
cross_disc_data2; default = None
cross_cont_data2; default = None
cross_cond_disc_data; default = None
cross_cond_cont_datal; default = None
covariance_multiplier; default = e**-1
quadrature_eval_number; default = 5
lambda_val; default = 1
Note that disc_data1, cont_data1 refer to discrete and continuous parts of X and
disc_data1, cont_data1 refer to discrete and continuous parts of Y for I(X;Y).

###KL_Divergence
This calculates the Kullback-Leibler Divergence.
Calculates KL-Divergence if no conditional data is provided.
Calculates Conditional KL-Divergence if conditional data is provided.
Corresponding Cross data must be provided.
Arguments:
disc_data; default = None
cont_data; default  = None
cond_disc_data; default = None
cond_cont_data; default = None
cross_disc_data; default = None
cross_cont_data; default = None
cross_cond_disc_data; default = None
cross_cond_cont_data; default = None

###Transfer Entropy

quadrature_eval_number; default = 5
lambda_val; default = 1