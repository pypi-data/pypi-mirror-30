# -*- coding: utf-8 -*-
"""
Created on Sun Mar 25 11:10:44 2018

@author: Peng
"""

import numpy
from scipy import linalg

###
###Errors
###

def Length_Error(disc_data,
                 cont_data,
                 var_index = None,
                 cross_bool = False):      
    
    if cross_bool == False:
        if var_index is None:
            error_message = 'Discrete and Continuous Data must correspond; require the same data length'
        else:
            error_message = (
                    'Discrete and Continuous Data must correspond; require the same data length. First error occurs in variable ' 
                    + str(var_index)
                    )
        
    else:
        if var_index is None:
            error_message = 'Discrete and Continuous Cross Data must correspond; require the same data length'
        else:
            error_message = (
                    'Discrete and Continuous Cross Data must correspond; require the same data length. First error occurs in cross variable ' 
                    + str(var_index)
                    )
    
    if cont_data is not None and disc_data is not None:
        if len(cont_data) != len(disc_data):
            raise ValueError(error_message)
            
def Multivar_Length_Error(data_tuple_list,
                          cross_bool = False):
    
    if cross_bool == False:
        error_message = 'Every variable must correspond; require same data length. Error occurs at variable index '
    else:
        error_message = 'Every cross variable must correspond; require same data length. Error occurs at cross variable index '
    
    tuple_list_length = len(data_tuple_list)
    
    if data_tuple_list[0][0] is None:
        data_length = len(data_tuple_list[0][1])
    else:
        data_length = len(data_tuple_list[0][0])
    
    for i in range(tuple_list_length):
        if data_tuple_list[i][0] is None and data_tuple_list[i][1] is not None:
            if len(data_tuple_list[i][1]) != data_length:
                raise ValueError(error_message + str(i))
        elif data_tuple_list[i][0] is not None and data_tuple_list[i][1] is None:
            if len(data_tuple_list[i][0]) != data_length:
                raise ValueError(error_message + str(i))
        Length_Error(disc_data = data_tuple_list[i][0],
                     cont_data = data_tuple_list[i][1],
                     var_index = i,
                     cross_bool = cross_bool)

def Cross_Error(disc_data,
                cont_data,
                cross_disc_data,
                cross_cont_data,
                var_index = None):
  
    if cross_disc_data is not None and disc_data is None:
        if var_index is None:
            raise ValueError('''Data and Cross Data must correspond; 
                             A  discrete cross data was specified with no discrete primary data.''')
        else:
            raise ValueError('''Data and Cross Data must correspond; 
                             A discrete cross data was specified with no discrete primary data. 
                             First Error occurs in variable''' + str(var_index))
            
    if cross_cont_data is not None and cont_data is None:
        if var_index is None:
            raise ValueError('''Data and Cross Data must correspond; 
                             A  continuous cross data was specified with no contintuous primary data.''')
        else:
            raise ValueError('''Data and Cross Data must correspond; 
                             A continuous cross data was specified with no continuous primary data. 
                             First Error occurs in variable''' + str(var_index))
            
def Cross_List_Error(disc_data,
                     cont_data,
                     cross_disc_data,
                     cross_cont_data,
                     var_index = None):
    
    if cross_disc_data is None and disc_data is not None:
        raise ValueError('''Data and Cross Data must correspond; 
                            A discrete primary data was specified with no discrete cross data. 
                            First Error occurs in variable''' + str(var_index))
            
    if cross_cont_data is not None and cont_data is None:
        raise ValueError('''Data and Cross Data must correspond; 
                            A continuous primary data was specified with no continuous cross data. 
                            First Error occurs in variable''' + str(var_index))    
            
def Multivar_Cross_Error(data_tuple_list,
                         cross_data_tuple_list):
    
    tuple_list_length = len(data_tuple_list)
    
    if cross_data_tuple_list is not None:
        for i in range(tuple_list_length):
            
            Cross_Error(disc_data = data_tuple_list[i][0],
                        cont_data = data_tuple_list[i][1],
                        cross_disc_data = cross_data_tuple_list[i][0],
                        cross_cont_data = cross_data_tuple_list[i][1],
                        var_index = i)
            Cross_List_Error(disc_data = data_tuple_list[i][0],
                             cont_data = data_tuple_list[i][1],
                             cross_disc_data = cross_data_tuple_list[i][0],
                             cross_cont_data = cross_data_tuple_list[i][1],
                             var_index = i)
    
    Multivar_Length_Error(data_tuple_list)
    
    if cross_data_tuple_list is not None:
        Multivar_Length_Error(cross_data_tuple_list,
                              cross_bool = True)
        

    
###
###Differential Entropy
###

###Initialising Gauss-Hermite Quadrature 

def Multivariate_Hermgauss(eval_number, dims):
    
    abscissa, weights = numpy.polynomial.hermite.hermgauss(eval_number)
    
    abscissa_array = numpy.array(numpy.meshgrid(*numpy.array([abscissa] * dims))).T.reshape(-1,dims)
    weights_array = numpy.array(numpy.meshgrid(*numpy.array([weights] * dims))).T.reshape(-1,dims)
    
    weights_vec = weights_array.prod(axis = 1)
    
    return abscissa_array, weights_vec

def Inner_Sum(cross_data,
              outer_shift,
              eval_point,
              cross_covar_matrix_inverse,
              orthogonal_matrix,
              sqrt_inv_eigenval_vec):
    
    quad_vec = 0
    
    outer_vec = (numpy.inner((2**0.5)*orthogonal_matrix, eval_point*sqrt_inv_eigenval_vec) +
                 outer_shift - cross_data)
        
        
    s = -0.5*(outer_vec.dot(cross_covar_matrix_inverse)*outer_vec)
    if len(s.shape) == 1:
        quad_vec += s
    else:
        quad_vec += s.sum(1)
        
    
    individual_exponentiated_vec = numpy.exp(quad_vec)
    inner_sum = individual_exponentiated_vec.sum()
    return inner_sum

def Inner_Log(cross_data,
              outer_shift,
              eval_point,
              cross_covar_matrix_inverse,
              orthogonal_matrix,
              sqrt_inv_eigenval_vec,
              inner_multiplier):
    log_target = inner_multiplier*Inner_Sum(cross_data,
                                      outer_shift,
                                      eval_point,
                                      cross_covar_matrix_inverse,
                                      orthogonal_matrix,
                                      sqrt_inv_eigenval_vec)
    
    return numpy.log(log_target)

def Herm_Sum_Inner_Log(cross_data,
                       hermgauss_point_array,
                       hermgauss_weight_vector,
                       outer_shift,
                       cross_covar_matrix_inverse,
                       orthogonal_matrix,
                       sqrt_inv_eigenval_vec,
                       inner_multiplier):
    
    herm_sum = 0
    
    for i in range(len(hermgauss_weight_vector)):
        
        eval_at_point = Inner_Log(cross_data,
              outer_shift,
              hermgauss_point_array[i],
              cross_covar_matrix_inverse,
              orthogonal_matrix,
              sqrt_inv_eigenval_vec,
              inner_multiplier)
        herm_sum += hermgauss_weight_vector[i]*eval_at_point 
    
    return herm_sum

def KD_Sum(cont_data,
           cross_data,
           hermgauss_point_array,
           hermgauss_weight_vector,
           cross_covar_matrix_inverse,
           orthogonal_matrix,
           sqrt_inv_eigenval_vec,
           inner_multiplier):
    
    kernel_density_herm_sum = 0
    
    for i in range(cont_data.shape[0]):
        kernel_density_herm_sum += Herm_Sum_Inner_Log(cross_data,
                                                      hermgauss_point_array,
                                                      hermgauss_weight_vector,
                                                      cont_data[i],
                                                      cross_covar_matrix_inverse,
                                                      orthogonal_matrix,
                                                      sqrt_inv_eigenval_vec,
                                                      inner_multiplier)
        
    return kernel_density_herm_sum

def Diff_Entropy(cont_data,
                 cross_data = None,
                 covariance_multiplier = 1,
                 quadrature_eval_number = 5,
                 discrete_probability = 1,
                 cross_discrete_probability = 1):
    
    ###cross_data is the data used for cross entropy
    
    ###Defining cross_data as cont_data if no cross data
    if cross_data is None:
        cross_data = cont_data
    
    ###Dimensions
    
    data_length = cont_data.shape[0]
    cross_data_length = cross_data.shape[0]
    
    if len(cont_data.shape) >= 2:
        dimensionality = len(cont_data[0])
    else:
        dimensionality = 1

    ###Hermite Quadrature Initialisation
    
    hermgauss_point_array, hermgauss_weight_vector = Multivariate_Hermgauss(quadrature_eval_number,
                                                                            dimensionality)
    
    ###Matrix Inititialisation
    
    covar_matrix = covariance_multiplier*numpy.cov(cont_data, rowvar = False)
    cross_covar_matrix = covariance_multiplier*numpy.cov(cross_data, rowvar = False)

    if dimensionality > 1:
        
        covar_matrix_inverse = numpy.linalg.inv(covar_matrix)
        orthogonal_matrix = linalg.orth(covar_matrix_inverse)
        diag_matrix = numpy.matmul(numpy.matmul(orthogonal_matrix.T, covar_matrix_inverse), orthogonal_matrix)
        eigenval_vec = numpy.diag(diag_matrix)
        covar_matrix_det = numpy.linalg.det(covar_matrix)
        orthogonal_matrix_det = abs(numpy.linalg.det(orthogonal_matrix))
        
        cross_covar_matrix_inverse = numpy.linalg.inv(cross_covar_matrix)
        cross_covar_matrix_det = numpy.linalg.det(cross_covar_matrix)
    
    else:
        covar_matrix_inverse = covar_matrix**-1
        orthogonal_matrix = 1
        diag_matrix = covar_matrix_inverse
        eigenval_vec = covar_matrix_inverse
        covar_matrix_det = covar_matrix
        orthogonal_matrix_det = 1
        
        cross_covar_matrix_inverse = cross_covar_matrix**-1
        cross_covar_matrix_det = cross_covar_matrix
    

    sqrt_inv_eigenval_vec = eigenval_vec**-0.5
    
    ###Multiplier

    
    numerator = (2**0.5)*orthogonal_matrix_det*discrete_probability
    
    denominator = data_length*((2*numpy.pi)**(0.5*dimensionality))*(covar_matrix_det**0.5)
    
    outer_multiplier = numerator/denominator
    
    inner_multiplier = (outer_multiplier*
                        ((covar_matrix_det/cross_covar_matrix_det)**0.5)*
                        (cross_discrete_probability/discrete_probability)*
                        (data_length/cross_data_length)/
                        (2**0.5))
    
    ###
    
    return -(covar_matrix_det**0.5)*outer_multiplier*KD_Sum(cont_data,
            cross_data,
            hermgauss_point_array,
            hermgauss_weight_vector,
            cross_covar_matrix_inverse,
            orthogonal_matrix,
            sqrt_inv_eigenval_vec,
            inner_multiplier)
    
    
###
###End of Differential Entropy
###
    
###
###Discrete
###
    
###Disc Class
    
class Disc_Partition:
    
    def __init__(self,disc_vals):
        
        self.vals = disc_vals
        self.data_indexes = list()
        self.cross_data_indexes = list()
        
    def __cont_partition__(self,cont_data, cross_cont_data):
        
        self.cont_subset = cont_data[self.data_indexes]
        self.cross_subset = cross_cont_data[self.cross_data_indexes]
        
    def __discrete_probability__(self, data_length, cross_data_length):
        
        self.disc_probability = len(self.data_indexes)/data_length
        self.cross_disc_probability = len(self.cross_data_indexes)/cross_data_length
        
###Bin Discrete/Categorical Data

def Disc_Bin(disc_data,
             cont_data = None,
             cross_disc_data = None,
             cross_cont_data = None):
    
    if cross_disc_data is None:
        cross_disc_data = disc_data
    
    if cross_cont_data is None:
        cross_cont_data = cont_data
        
    data_length = len(disc_data)
    cross_data_length = len(cross_disc_data)
        
    discrete_set = {}
    
    ###Add Data indexes to subsets
    
    if type(disc_data[0]) == numpy.ndarray:
    
        for i in range(data_length):
        
            if tuple(disc_data[i]) not in discrete_set:
                
                discrete_set[tuple(disc_data[i])] = Disc_Partition(tuple(disc_data[i]))
                discrete_set[tuple(disc_data[i])].data_indexes.append(i)
                
            else:
                
                discrete_set[tuple(disc_data[i])].data_indexes.append(i)
                
    else:
        
        for i in range(data_length):
        
            if disc_data[i] not in discrete_set:
                
                discrete_set[disc_data[i]] = Disc_Partition(disc_data[i])
                discrete_set[disc_data[i]].data_indexes.append(i)
                
            else:
                
                discrete_set[disc_data[i]].data_indexes.append(i)    
    
    ###Add Cross Data indexes to subsets
    
    if type(disc_data[0]) == numpy.ndarray:
    
        for i in range(data_length):
        
            if tuple(cross_disc_data[i]) not in discrete_set:
                
                discrete_set[tuple(cross_disc_data[i])] = Disc_Partition(tuple(cross_disc_data[i]))
                discrete_set[tuple(cross_disc_data[i])].cross_data_indexes.append(i)
                
            else:
                
                discrete_set[tuple(cross_disc_data[i])].cross_data_indexes.append(i)
                
    else:
        
        for i in range(data_length):
        
            if cross_disc_data[i] not in discrete_set:
                
                discrete_set[cross_disc_data[i]] = Disc_Partition(cross_disc_data[i])
                discrete_set[cross_disc_data[i]].cross_data_indexes.append(i)
                
            else:
                discrete_set[cross_disc_data[i]].cross_data_indexes.append(i)   
    
    ###Add data subsets
    
    for subset in discrete_set:
        if cont_data is not None:
            discrete_set[subset].__cont_partition__(cont_data, cross_cont_data)

        discrete_set[subset].__discrete_probability__(data_length, cross_data_length)
   
    return discrete_set

###
###Mixed Entropy
###

def Entropy(disc_data = None,
            cont_data = None,
            cross_disc_data = None,
            cross_cont_data = None,
            covariance_multiplier = numpy.exp(-1),
            quadrature_eval_number = 5):
    
    Length_Error(disc_data = disc_data,
                 cont_data = cont_data,
                 var_index = None,
                 cross_bool = False)
    
    Length_Error(disc_data = cross_disc_data,
                 cont_data = cross_cont_data,
                 var_index = None,
                 cross_bool = True)
    
    Cross_Error(disc_data = disc_data,
                cont_data = cont_data,
                cross_disc_data = cross_disc_data,
                cross_cont_data = cross_cont_data,
                var_index = None)
    
    if cross_disc_data is None:
        cross_disc_data = disc_data
        
    if cross_cont_data is None:
        cross_cont_data = cont_data
        
    
    if disc_data is None:
        
        entropy =  Diff_Entropy(cont_data = cont_data,
                                cross_data = cross_cont_data,
                                covariance_multiplier = covariance_multiplier,
                                quadrature_eval_number = quadrature_eval_number)
    

    else:
        
        disc_partition_dictionary = Disc_Bin(disc_data = disc_data,
                                             cont_data = cont_data,
                                             cross_disc_data = cross_disc_data,
                                             cross_cont_data = cross_cont_data)
        
        entropy = 0
        
        if cont_data is None:
            for subset in disc_partition_dictionary:
                
                entropy += (
                        -(disc_partition_dictionary[subset].disc_probability
                          *numpy.log(disc_partition_dictionary[subset].cross_disc_probability))
                        )
    
        else:
            for subset in disc_partition_dictionary:
                
                entropy += Diff_Entropy(cont_data = cont_data,
                                        cross_data = cross_cont_data,
                                        covariance_multiplier = covariance_multiplier,
                                        quadrature_eval_number = quadrature_eval_number,
                                        discrete_probability = disc_partition_dictionary[subset].disc_probability,
                                        cross_discrete_probability = disc_partition_dictionary[subset].cross_disc_probability)
                
    return entropy

###
###End Entropy
###
   
###Reshape and Concatenate Data Lists
def Merge_Data(disc_data_cont_data_tuple_list,
               cross_disc_data_cont_data_tuple_list = None):
    
    Multivar_Cross_Error(data_tuple_list = disc_data_cont_data_tuple_list,
                         cross_data_tuple_list = cross_disc_data_cont_data_tuple_list)
    
    tuple_number = len(disc_data_cont_data_tuple_list)

    ###Length of Data
    if cross_disc_data_cont_data_tuple_list is None:
        cross_disc_data_cont_data_tuple_list = disc_data_cont_data_tuple_list
    
    for i in range(tuple_number):

        if disc_data_cont_data_tuple_list[i][0] is not None:
            data_length = len(disc_data_cont_data_tuple_list[i][0])
            cross_data_length = len(cross_disc_data_cont_data_tuple_list[i][0])
            break
        if disc_data_cont_data_tuple_list[i][1] is not None:
            data_length = len(disc_data_cont_data_tuple_list[i][1])
            cross_data_length = len(cross_disc_data_cont_data_tuple_list[i][1])
            break
     
    ###Reshaping to allow for concatenation
            
    ###Reshaping Data
    
    for i in range(tuple_number):
        if disc_data_cont_data_tuple_list[i][0] is not None:
            if len(disc_data_cont_data_tuple_list[i][0].shape) < 2:
                dummy_disc = (disc_data_cont_data_tuple_list[i][0]
                .reshape(
                        [disc_data_cont_data_tuple_list[i][0].shape[0], 1]
                        )
                )
            else:
               dummy_disc = disc_data_cont_data_tuple_list[i][0]
        else:
            dummy_disc = disc_data_cont_data_tuple_list[i][0]
               
        if disc_data_cont_data_tuple_list[i][1] is not None:
            if len(disc_data_cont_data_tuple_list[i][1].shape) < 2:
                dummy_cont = (disc_data_cont_data_tuple_list[i][1]
                .reshape(
                        [disc_data_cont_data_tuple_list[i][1].shape[0], 1]
                        )
                )
            else:
               dummy_cont = disc_data_cont_data_tuple_list[i][1]
        else:
            dummy_cont = disc_data_cont_data_tuple_list[i][1]
            
        disc_data_cont_data_tuple_list[i] = (dummy_disc, dummy_cont)

    ###Reshaping Cross Data

        if cross_disc_data_cont_data_tuple_list[i][0] is not None:
            if len(cross_disc_data_cont_data_tuple_list[i][0].shape) < 2:
                dummy_cross_disc = (cross_disc_data_cont_data_tuple_list[i][0]
                .reshape(
                        [cross_disc_data_cont_data_tuple_list[i][0].shape[0], 1]
                        )
                )
            else:
               dummy_cross_disc = cross_disc_data_cont_data_tuple_list[i][0]
        else:
            dummy_cross_disc = cross_disc_data_cont_data_tuple_list[i][0]
               
        if cross_disc_data_cont_data_tuple_list[i][1] is not None:
            if len(cross_disc_data_cont_data_tuple_list[i][1].shape) < 2:
                dummy_cross_cont = (cross_disc_data_cont_data_tuple_list[i][1]
                .reshape(
                        [cross_disc_data_cont_data_tuple_list[i][1].shape[0], 1]
                        )
                )
            else:
               dummy_cross_cont = cross_disc_data_cont_data_tuple_list[i][1]
        else:
            dummy_cross_cont = cross_disc_data_cont_data_tuple_list[i][1]
    
    
        cross_disc_data_cont_data_tuple_list[i] = (dummy_cross_disc, dummy_cross_cont)
    
    ###Concatenating Data    
    
    joint_disc_data = numpy.zeros([data_length,0])
    joint_cont_data = numpy.zeros([data_length,0])
    
    cross_joint_disc_data = numpy.zeros([cross_data_length,0])
    cross_joint_cont_data = numpy.zeros([cross_data_length,0])
    
    for i in range(tuple_number):
        
        if disc_data_cont_data_tuple_list[i][0] is not None:
            joint_disc_data = numpy.concatenate((joint_disc_data, disc_data_cont_data_tuple_list[i][0]),
                              axis = 1)
        if disc_data_cont_data_tuple_list[i][1] is not None:
            joint_cont_data = numpy.concatenate((joint_cont_data, disc_data_cont_data_tuple_list[i][1]),
                              axis = 1)
            
        if cross_disc_data_cont_data_tuple_list[i][0] is not None:
            cross_joint_disc_data = numpy.concatenate((cross_joint_disc_data, cross_disc_data_cont_data_tuple_list[i][0]), axis = 1)
        if disc_data_cont_data_tuple_list[i][1] is not None:
            cross_joint_cont_data = numpy.concatenate((cross_joint_cont_data, cross_disc_data_cont_data_tuple_list[i][1]), axis = 1)
            
    if joint_disc_data.shape[1] == 0:
        joint_disc_data = None
    if joint_cont_data.shape[1] == 0:
        joint_cont_data = None
        
    if cross_joint_disc_data.shape[1] == 0:
        cross_joint_disc_data = None
    if cross_joint_cont_data.shape[1] == 0:
        cross_joint_cont_data = None

    return (joint_disc_data,
            joint_cont_data,
            cross_joint_disc_data,
            cross_joint_cont_data)
###
###Entropy Extensions
###


###Joint Entropy
def Joint_Entropy(disc_data_cont_data_tuple_list,
                  cross_disc_data_cont_data_tuple_list = None,
                  covariance_multiplier = numpy.exp(-1),
                  quadrature_eval_number = 5):
    
    Multivar_Cross_Error(data_tuple_list = disc_data_cont_data_tuple_list,
                         cross_data_tuple_list = cross_disc_data_cont_data_tuple_list)
    
    if cross_disc_data_cont_data_tuple_list is None:
        cross_disc_data_cont_data_tuple_list = disc_data_cont_data_tuple_list
    
    (joint_disc_data,
     joint_cont_data,
     cross_joint_disc_data,
     cross_joint_cont_data) = Merge_Data(disc_data_cont_data_tuple_list,
                              cross_disc_data_cont_data_tuple_list)
       
    return Entropy(disc_data = joint_disc_data,
                   cont_data = joint_cont_data,
                   cross_disc_data = cross_joint_disc_data,
                   cross_cont_data = cross_joint_cont_data,
                   covariance_multiplier = covariance_multiplier,
                   quadrature_eval_number = quadrature_eval_number)

def Conditional_Entropy(disc_data = None,
                        cont_data = None,
                        cond_disc_data = None,
                        cond_cont_data = None,
                        cross_disc_data = None,
                        cross_cont_data = None,
                        cross_cond_disc_data = None,
                        cross_cond_cont_data = None,
                        covariance_multiplier = numpy.exp(-1),
                        quadrature_eval_number = 5):
    
    Length_Error(disc_data = disc_data,
                 cont_data = cont_data,
                 var_index = None,
                 cross_bool = False)
    
    Length_Error(disc_data = cross_disc_data,
                 cont_data = cross_cont_data,
                 var_index = None,
                 cross_bool = True)
    
    Cross_Error(disc_data = disc_data,
                cont_data = cont_data,
                cross_disc_data = cross_disc_data,
                cross_cont_data = cross_cont_data,
                var_index = None)
    
    data_tuple_list = [(disc_data, cont_data), (cond_disc_data, cond_cont_data)]
    if (cross_disc_data is None and
        cross_cont_data is None and
        cross_cond_disc_data is None and
        cross_cond_cont_data is None):
            cross_data_tuple_list = data_tuple_list

    else:
        cross_data_tuple_list = [(cross_disc_data, cross_cont_data), (cross_cond_disc_data, cross_cond_cont_data)]
    
    joint_entropy = Joint_Entropy(disc_data_cont_data_tuple_list = data_tuple_list,
                                   cross_disc_data_cont_data_tuple_list = cross_data_tuple_list,
                                   covariance_multiplier = covariance_multiplier,
                                   quadrature_eval_number = quadrature_eval_number)
    
    if cond_disc_data is not None and cond_cont_data is not None:
        cond_var_entropy = Entropy(disc_data = cond_disc_data,
                                   cont_data = cond_cont_data,
                                   cross_disc_data = cross_cond_disc_data,
                                   cross_cont_data = cross_cond_cont_data,
                                   covariance_multiplier = covariance_multiplier,
                                   quadrature_eval_number = quadrature_eval_number)
    
    else: cond_var_entropy = 0
    
    return joint_entropy - cond_var_entropy

def Total_Correlation(disc_data_cont_data_tuple_list,
                      cross_disc_data_cont_data_tuple_list = None,
                      cond_disc_data = None,
                      cond_cont_data = None,
                      cross_cond_disc_data = None,
                      cross_cond_cont_data = None,
                      covariance_multiplier = numpy.exp(-1),
                      quadrature_eval_number = 5,
                      max_return = False):
    
    Multivar_Cross_Error(data_tuple_list = disc_data_cont_data_tuple_list,
                         cross_data_tuple_list = cross_disc_data_cont_data_tuple_list)
    
    tuple_number = len(disc_data_cont_data_tuple_list)
    
    individual_entropy_sum = 0
    
    if cross_disc_data_cont_data_tuple_list is None:
        cross_disc_data_cont_data_tuple_list = disc_data_cont_data_tuple_list
    
    for i in range(tuple_number):
        individual_entropy = Conditional_Entropy(disc_data = disc_data_cont_data_tuple_list[i][0],
                                                 cont_data = disc_data_cont_data_tuple_list[i][1],
                                                 cond_disc_data = cond_disc_data,
                                                 cond_cont_data = cond_cont_data,
                                                 cross_disc_data = cross_disc_data_cont_data_tuple_list[i][0],
                                                 cross_cont_data = cross_disc_data_cont_data_tuple_list[i][1],
                                                 cross_cond_disc_data = cross_cond_disc_data,
                                                 cross_cond_cont_data = cross_cond_cont_data,
                                                 covariance_multiplier = covariance_multiplier,
                                                 quadrature_eval_number = quadrature_eval_number)
        
        individual_entropy_sum += individual_entropy
        if i == 0:
            max_individual = individual_entropy
        else:
            if individual_entropy > max_individual:
                max_individual = individual_entropy
        
    (joint_disc_data,
     joint_cont_data,
     cross_joint_disc_data,
     cross_joint_cont_data) = Merge_Data(disc_data_cont_data_tuple_list,
                                 cross_disc_data_cont_data_tuple_list)
    
    
    joint_entropy = Conditional_Entropy(disc_data = joint_disc_data,
                                        cont_data = joint_cont_data,
                                        cond_disc_data = cond_disc_data,
                                        cond_cont_data = cond_cont_data,
                                        cross_disc_data = cross_joint_disc_data,
                                        cross_cont_data = cross_joint_cont_data,
                                        cross_cond_disc_data = cross_cond_disc_data,
                                        cross_cond_cont_data = cross_cond_cont_data,
                                        covariance_multiplier = covariance_multiplier,
                                        quadrature_eval_number = quadrature_eval_number)
    
    if max_return:
        return (individual_entropy_sum - joint_entropy, max_individual)
    else:
        return individual_entropy_sum - joint_entropy

def Mutual_Information(disc_data1 = None,
                       cont_data1 = None,
                       disc_data2 = None,
                       cont_data2 = None,
                       cond_disc_data = None,
                       cond_cont_data = None,
                       cross_disc_data1 = None,
                       cross_cont_data1 = None,
                       cross_disc_data2 = None,
                       cross_cont_data2 = None,                       
                       cross_cond_disc_data = None,
                       cross_cond_cont_data = None,
                       covariance_multiplier = numpy.exp(-1),
                       quadrature_eval_number = 5):
    
    tuple_list = [(disc_data1, cont_data1),(disc_data2, cont_data2)]
    cross_tuple_list = [(cross_disc_data1, cross_cont_data1),(cross_disc_data2, cross_disc_data1)]
    if cross_tuple_list == [(None, None), (None, None)]:
        cross_tuple_list = tuple_list
    return Total_Correlation(disc_data_cont_data_tuple_list = tuple_list,
                             cross_disc_data_cont_data_tuple_list = cross_tuple_list,
                             cond_disc_data = None,
                             cond_cont_data = None,
                             cross_cond_disc_data = None,
                             cross_cond_cont_data = None,
                             covariance_multiplier = covariance_multiplier,
                             quadrature_eval_number = quadrature_eval_number)
    
def Variation_Of_Information(disc_data1 = None,
                             cont_data1 = None,
                             disc_data2 = None,
                             cont_data2 = None,
                             cond_disc_data = None,
                             cond_cont_data = None,
                             cross_disc_data1 = None,
                             cross_cont_data1 = None,
                             cross_disc_data2 = None,
                             cross_cont_data2 = None,                       
                             cross_cond_disc_data = None,
                             cross_cond_cont_data = None,
                             covariance_multiplier = numpy.exp(-1),
                             quadrature_eval_number = 5):
    
    tuple_list = [(disc_data1, cont_data1),(disc_data2, cont_data2)]
    cross_tuple_list = [(cross_disc_data1, cross_cont_data1),(cross_disc_data2, cross_disc_data1)]
    
    first_individual_entropy = Conditional_Entropy(disc_data = tuple_list[0][0],
                                                   cont_data = tuple_list[0][1],
                                                   cond_disc_data = cond_disc_data,
                                                   cond_cont_data = cond_cont_data,
                                                   cross_disc_data = cross_tuple_list[0][0],
                                                   cross_cont_data = cross_tuple_list[0][1],
                                                   cross_cond_disc_data = cross_cond_disc_data,
                                                   cross_cond_cont_data = cross_cond_cont_data,
                                                   covariance_multiplier = covariance_multiplier,
                                                   quadrature_eval_number = quadrature_eval_number)
    
    second_individual_entropy = Conditional_Entropy(disc_data = tuple_list[1][0],
                                                    cont_data = tuple_list[1][1],
                                                    cond_disc_data = cond_disc_data,
                                                    cond_cont_data = cond_cont_data,
                                                    cross_disc_data = cross_tuple_list[1][0],
                                                    cross_cont_data = cross_tuple_list[1][1],
                                                    cross_cond_disc_data = cross_cond_disc_data,
                                                    cross_cond_cont_data = cross_cond_cont_data,
                                                    covariance_multiplier = covariance_multiplier,
                                                    quadrature_eval_number = quadrature_eval_number)
    
    double_joint_entropy = 2*Mutual_Information(disc_data1 = disc_data1,
                                                cont_data1 = cont_data1,
                                                disc_data2 = disc_data2,
                                                cont_data2 = cont_data2,
                                                cond_disc_data = cond_disc_data,
                                                cond_cont_data = cond_cont_data,
                                                cross_disc_data1 = cross_disc_data1,
                                                cross_cont_data1 = cross_cont_data1,
                                                cross_disc_data2 = cross_disc_data2,
                                                cross_cont_data2 = cross_cont_data2,                       
                                                cross_cond_disc_data = cross_cond_disc_data,
                                                cross_cond_cont_data = cross_cond_cont_data,
                                                covariance_multiplier = covariance_multiplier,
                                                quadrature_eval_number = quadrature_eval_number)
    
    return double_joint_entropy - first_individual_entropy - second_individual_entropy

def KL_Divergence(disc_data = None,
                  cont_data = None,
                  cond_disc_data = None,
                  cond_cont_data = None,
                  cross_disc_data = None,
                  cross_cont_data = None,
                  cross_cond_disc_data = None,
                  cross_cond_cont_data = None,
                  covariance_multiplier = numpy.exp(-1),
                  quadrature_eval_number = 5):
    
    if cross_disc_data is None and cross_cont_data is None:
        raise ValueError('Cross data must be provided for KL_Divergence')
    
    cross_entropy = Conditional_Entropy(disc_data = disc_data,
                                        cont_data = cont_data,
                                        cond_disc_data = cond_disc_data,
                                        cond_cont_data = cond_cont_data,
                                        cross_disc_data = cross_disc_data,
                                        cross_cont_data = cross_cont_data,
                                        cross_cond_disc_data = cross_cond_disc_data,
                                        cross_cond_cont_data = cross_cond_cont_data,
                                        covariance_multiplier = covariance_multiplier,
                                        quadrature_eval_number = quadrature_eval_number)
    
    base_entropy = Conditional_Entropy(disc_data = disc_data,
                                        cont_data = cont_data,
                                        cond_disc_data = cond_disc_data,
                                        cond_cont_data = cond_cont_data,
                                        cross_disc_data = None,
                                        cross_cont_data = None,
                                        cross_cond_disc_data = None,
                                        cross_cond_cont_data = None,
                                        covariance_multiplier = covariance_multiplier,
                                        quadrature_eval_number = quadrature_eval_number)
    
    return cross_entropy - base_entropy

def Symmetric_KL_Divergence(disc_data = None,
                            cont_data = None,
                            cond_disc_data = None,
                            cond_cont_data = None,
                            cross_disc_data = None,
                            cross_cont_data = None,
                            cross_cond_disc_data = None,
                            cross_cond_cont_data = None,
                            covariance_multiplier = 1,
                            quadrature_eval_number = 5):

    if cross_disc_data is None and cross_cont_data is None:
        raise ValueError('Cross data must be provided for Symmetric_KL_Divergence')
    
    kl_div = KL_Divergence(disc_data = disc_data,
                           cont_data = cont_data,
                           cond_disc_data = cond_disc_data,
                           cond_cont_data = cond_cont_data,
                           cross_disc_data = cross_disc_data,
                           cross_cont_data = cross_cont_data,
                           cross_cond_disc_data = cross_cond_disc_data,
                           cross_cond_cont_data = cross_cond_cont_data,
                           covariance_multiplier = covariance_multiplier,
                           quadrature_eval_number = quadrature_eval_number)
    
    cross_kl_div = KL_Divergence(disc_data = cross_disc_data,
                                 cont_data = cross_cont_data,
                                 cond_disc_data = cross_cond_disc_data,
                                 cond_cont_data = cross_cond_cont_data,
                                 cross_disc_data = disc_data,
                                 cross_cont_data = cont_data,
                                 cross_cond_disc_data = cond_disc_data,
                                 cross_cond_cont_data = cond_cont_data,
                                 covariance_multiplier = covariance_multiplier,
                                 quadrature_eval_number = quadrature_eval_number)
    
    return kl_div + cross_kl_div


def TE_Subsetting(data, skip_number, window, iteration):
    if data is None:
        return None
    elif window is not None:
        return data[skip_number + iteration:skip_number + iteration + window]
    else:
        return data[skip_number + iteration:]
    
def Information_Storage(disc_data = None,
                        cont_data = None,
                        cond_disc_data = None,
                        cond_cont_data = None,
                        history_length = 1,
                        history_delay = 1,
                        window_size = None,
                        window_skip = None,
                        cross_disc_data = None,
                        cross_cont_data = None,
                        cross_cond_disc_data = None,
                        cross_cond_cont_data = None,
                        covariance_multiplier = numpy.exp(-1),
                        quadrature_eval_number = 5):
    
    ###T_{X->Y} = I(Y_{t};X_{t-1:t-L} | Y_{t-1:t-L})
    
    if disc_data is not None:
        data_length = len(disc_data)
    else:
        data_length = len(cont_data)
    
    if cross_source_disc_data is not None:
        cross_data_length = len(cross_disc_data)
    else:
        cross_data_length = len(cross_cont_data)
    
    tuple_list = list()
    cross_tuple_list = list()
    
    ###Data
    
    for i in range(history_length):
        
        ###Source
        
        if disc_data is not None:
            disc_history = disc_data[i*history_delay:data_length - (history_length - i)*history_delay]
        else:
            source_disc_history = None
            
        if cont_data is not None:
            cont_history = cont_data[i*history_delay:data_length - (history_length - i)*history_delay]
        else:
            cont_history = None
            
        tuple_list.append((disc_history, cont_history))
    
    ###Cross Data
    
    for i in range(history_length):
        
        ###Source
        
        if cross_disc_data is not None:
            cross_disc_history = cross_disc_data[i*history_delay:cross_data_length - (history_length - i)*history_delay]
        else:
            cross_disc_history = None
            
        if cross_cont_data is not None:
            cross_cont_history = cross_cont_data[i*history_delay:cross_data_length - (history_length - i)*history_delay]
        else:
            cross_source_cont_history = None
    
        cross_tuple_list.append((cross_source_disc_history, cross_source_cont_history))
    
    if (cross_disc_data is None and
        cross_cont_data is None and
        cross_cond_disc_data is None and
        cross_cond_cont_data is None):
        cross_tuple_list = tuple_list
    
    skip_number = history_length*history_delay    
        
    tuple_list.append((TE_Subsetting(cond_disc_data, skip_number, None, 0), 
                              TE_Subsetting(cond_cont_data, skip_number, None, 0)))
    cross_tuple_list.append((TE_Subsetting(cross_cond_disc_data, skip_number, None, 0),
                                    TE_Subsetting(cross_cond_cont_data, skip_number, None, 0)))
    
    (joint_disc_data,
     joint_cont_data,
     cross_joint_disc_data,
     cross_joint_cont_data) = Merge_Data(tuple_list,
                          cross_tuple_list)

    
    skip_number = history_length*history_delay
    
    if window_size is None:
        window_size = data_length - skip_number
    
    if window_skip is None:
        window_skip = 1
    
    window_te_list = list()
    for i in range(data_length - window_size):
        if i % window_skip == 0:
            window_te = Conditional_Entropy(disc_data = TE_Subsetting(disc_data, skip_number, window_size, i),
                                            cont_data = TE_Subsetting(cont_data, skip_number, window_size, i),
                                            cond_disc_data = TE_Subsetting(joint_disc_data, 0, window_size, i),
                                            cond_cont_data = TE_Subsetting(joint_cont_data, 0, window_size, i),
                                            cross_disc_data = TE_Subsetting(cross_disc_data, skip_number, window_size, i),
                                            cross_cont_data = TE_Subsetting(cross_cont_data, skip_number, window_size, i),                     
                                            cross_cond_disc_data = TE_Subsetting(cross_joint_disc_data, 0, window_size, i),
                                            cross_cond_cont_data = TE_Subsetting(cross_joint_cont_data, 0, window_size, i),
                                            covariance_multiplier = covariance_multiplier,
                                            quadrature_eval_number = quadrature_eval_number)
            window_te_list.append(window_te)
    return window_te_list

def Transfer_Entropy(source_disc_data = None,
                     source_cont_data = None,
                     target_disc_data = None,
                     target_cont_data = None,
                     cond_disc_data = None,
                     cond_cont_data = None,
                     history_length = 1,
                     history_delay = 1,
                     window_size = None,
                     window_skip = None,
                     cross_source_disc_data = None,
                     cross_source_cont_data = None,
                     cross_target_disc_data = None,
                     cross_target_cont_data = None,
                     cross_cond_disc_data = None,
                     cross_cond_cont_data = None,
                     covariance_multiplier = numpy.exp(-1),
                     quadrature_eval_number = 5):
    
    ###T_{X->Y} = I(Y_{t};X_{t-1:t-L} | Y_{t-1:t-L})
    
    if source_disc_data is not None:
        data_length = len(source_disc_data)
    else:
        data_length = len(source_cont_data)
    
    if cross_source_disc_data is not None:
        cross_data_length = len(source_disc_data)
    else:
        cross_data_length = len(source_cont_data)
    
    source_tuple_list = list()
    source_cross_tuple_list = list()
    target_tuple_list = list()
    target_cross_tuple_list = list()
    
    ###Data
    
    for i in range(history_length):
        
        ###Source
        
        if source_disc_data is not None:
            source_disc_history = source_disc_data[i*history_delay:data_length - (history_length - i)*history_delay]
        else:
            source_disc_history = None
            
        if source_cont_data is not None:
            source_cont_history = source_cont_data[i*history_delay:data_length - (history_length - i)*history_delay]
        else:
            source_cont_history = None
            
        ###Target
            
        if target_disc_data is not None:
            target_disc_history = target_disc_data[i*history_delay:data_length - (history_length - i)*history_delay]
        else:
            target_disc_history = None
            
        if target_cont_data is not None:
            target_cont_history = source_cont_data[i*history_delay:data_length - (history_length - i)*history_delay]
        else:
            target_cont_history = None
            
        source_tuple_list.append((source_disc_history, source_cont_history))
        target_tuple_list.append((target_disc_history, target_cont_history))
    
    ###Cross Data
    
    for i in range(history_length):
        
        ###Source
        
        if cross_source_disc_data is not None:
            cross_source_disc_history = cross_source_disc_data[i*history_delay:cross_data_length - (history_length - i)*history_delay]
        else:
            cross_source_disc_history = None
            
        if cross_source_cont_data is not None:
            cross_source_cont_history = cross_source_cont_data[i*history_delay:cross_data_length - (history_length - i)*history_delay]
        else:
            cross_source_cont_history = None
    
        ###Target
    
        if cross_target_disc_data is not None:
            cross_target_disc_history = cross_target_disc_data[i*history_delay:cross_data_length - (history_length - i)*history_delay]
        else:
            cross_target_disc_history = None
            
        if cross_source_cont_data is not None:
            cross_target_cont_history = cross_target_cont_data[i*history_delay:cross_data_length - (history_length - i)*history_delay]
        else:
            cross_target_cont_history = None
    
        source_cross_tuple_list.append((cross_source_disc_history, cross_source_cont_history))
        target_cross_tuple_list.append((cross_target_disc_history, cross_target_cont_history))
    
    if (cross_source_disc_data is None and
        cross_source_cont_data is None and
        cross_target_disc_data is None and
        cross_target_cont_data is None and
        cross_cond_disc_data is None and
        cross_cond_cont_data is None):
        
        (source_cross_tuple_list,
         target_cross_tuple_list) = (source_tuple_list,
                                target_tuple_list)
    
    skip_number = history_length*history_delay    
        
    target_tuple_list.append((TE_Subsetting(cond_disc_data, skip_number, None, 0), 
                              TE_Subsetting(cond_cont_data, skip_number, None, 0)))
    target_cross_tuple_list.append((TE_Subsetting(cross_cond_disc_data, skip_number, None, 0),
                                    TE_Subsetting(cross_cond_cont_data, skip_number, None, 0)))
    
    (joint_target_disc_data,
     joint_target_cont_data,
     cross_joint_target_disc_data,
     cross_joint_target_cont_data) = Merge_Data(target_tuple_list,
                                 target_cross_tuple_list)
    
    (joint_source_disc_data,
     joint_source_cont_data,
     cross_joint_source_disc_data,
     cross_joint_source_cont_data) = Merge_Data(source_tuple_list,
                                  source_cross_tuple_list) 
    
    skip_number = history_length*history_delay
    
    if window_size is None:
        window_size = data_length - skip_number
    
    if window_skip is None:
        window_skip = 1
    
    window_te_list = list()
    for i in range(data_length - window_size):
        if i % window_skip == 0:
            window_te = Mutual_Information(disc_data1 = TE_Subsetting(target_disc_data, skip_number, window_size, i),
                                           cont_data1 = TE_Subsetting(target_cont_data, skip_number, window_size, i),
                                           disc_data2 = TE_Subsetting(joint_source_disc_data, 0, window_size, i),
                                           cont_data2 = TE_Subsetting(joint_source_cont_data, 0, window_size, i),
                                           cond_disc_data = TE_Subsetting(joint_target_disc_data, 0, window_size, i),
                                           cond_cont_data = TE_Subsetting(joint_target_cont_data, 0, window_size, i),
                                           cross_disc_data1 = TE_Subsetting(cross_target_disc_data, skip_number, window_size, i),
                                           cross_cont_data1 = TE_Subsetting(cross_target_cont_data, skip_number, window_size, i),
                                           cross_disc_data2 = TE_Subsetting(cross_joint_source_disc_data, 0, window_size, i),
                                           cross_cont_data2 = TE_Subsetting(cross_joint_source_cont_data, 0, window_size, i),                       
                                           cross_cond_disc_data = TE_Subsetting(cross_joint_target_disc_data, 0, window_size, i),
                                           cross_cond_cont_data = TE_Subsetting(cross_joint_source_cont_data, 0, window_size, i),
                                           covariance_multiplier = covariance_multiplier,
                                           quadrature_eval_number = quadrature_eval_number)
            window_te_list.append(window_te)
    return window_te_list