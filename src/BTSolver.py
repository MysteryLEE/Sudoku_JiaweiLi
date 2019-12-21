import SudokuBoard
import Variable
import Domain
import Trail
import Constraint
import ConstraintNetwork
import time
import random

class BTSolver:

    # ==================================================================
    # Constructors
    # ==================================================================

    def __init__ ( self, gb, trail, val_sh, var_sh, cc ):
        self.network = ConstraintNetwork.ConstraintNetwork(gb)
        self.hassolution = False
        self.gameboard = gb
        self.trail = trail

        self.varHeuristics = var_sh
        self.valHeuristics = val_sh
        self.cChecks = cc

    # ==================================================================
    # Consistency Checks
    # ==================================================================

    # Basic consistency check, no propagation done
    def assignmentsCheck ( self ):
        for c in self.network.getConstraints():
            if not c.isConsistent():
                return False
        return True

    """
        Part 1 TODO: Implement the Forward Checking Heuristic

        This function will do both Constraint Propagation and check
        the consistency of the network

        (1) If a variable is assigned then eliminate that value from
            the square's neighbors.

        Note: remember to trail.push variables before you assign them
        Return: a tuple of a dictionary and a bool. The dictionary contains all MODIFIED variables, mapped to their MODIFIED domain.
                The bool is true if assignment is consistent, false otherwise.
    """
    def forwardChecking ( self ):
        my_dict={}
        mConstraints=self.network.getModifiedConstraints()
        for mConstraint in mConstraints:
            if not mConstraint.isConsistent():
                return (my_dict,False)
            for var in mConstraint.vars:
                if var.isAssigned():
                    neighbors=self.network.getNeighborsOfVariable(var)  #check all its unassigned neighbors
                    for neighbor in neighbors:
                        if not neighbor.isAssigned():
                            for value in neighbor.getValues():
                                if value==var.getAssignment():   #modify the neighbor's domain
                                    self.trail.push(neighbor)
                                    neighbor.removeValueFromDomain(value)
                                    my_dict[neighbor]=neighbor.getDomain()
        if my_dict:  #if any neighbor's domain has been modified
            for value in my_dict.values():  #check if one's domain is empty.
                if value.size()==0:
                    return (my_dict,False)
        return (my_dict,True)

    # =================================================================
	# Arc Consistency
	# =================================================================
    def arcConsistency( self ):
        assignedVars = []
        for c in self.network.constraints:
            for v in c.vars:
                if v.isAssigned():
                    assignedVars.append(v)
        while len(assignedVars) != 0:
            av = assignedVars.pop(0)
            for neighbor in self.network.getNeighborsOfVariable(av):
                if neighbor.isChangeable and not neighbor.isAssigned() and neighbor.getDomain().contains(av.getAssignment()):
                    neighbor.removeValueFromDomain(av.getAssignment())
                    if neighbor.domain.size() == 1:
                        neighbor.assignValue(neighbor.domain.values[0])
                        assignedVars.append(neighbor)

    
    """
        Part 2 TODO: Implement both of Norvig's Heuristics

        This function will do both Constraint Propagation and check
        the consistency of the network

        (1) If a variable is assigned then eliminate that value from
            the square's neighbors.

        (2) If a constraint has only one possible place for a value
            then put the value there.

        Note: remember to trail.push variables before you assign them
        Return: a pair of a dictionary and a bool. The dictionary contains all variables 
		        that were ASSIGNED during the whole NorvigCheck propagation, and mapped to the values that they were assigned.
                The bool is true if assignment is consistent, false otherwise.
    """
    def norvigCheck ( self ):
        my_dict={}
        mConstraints=self.network.getModifiedConstraints()
        for mConstraint in mConstraints:
            if not mConstraint.isConsistent():
                return (my_dict,False)
            for var in mConstraint.vars:
                if var.isAssigned():
                    neighbors=self.network.getNeighborsOfVariable(var)  #check all its unassigned neighbors
                    for neighbor in neighbors:
                        if not neighbor.isAssigned():
                            for value in neighbor.getValues():
                                if value==var.getAssignment():   #modify the neighbor's domain
                                    self.trail.push(neighbor)
                                    neighbor.removeValueFromDomain(value)
                                    #my_dict[neighbor]=neighbor.getDomain()
        if my_dict:  #if any neighbor's domain has been modified
            for value in my_dict.values():  #check if one's domain is empty.
                if value.size()==0:
                    return (my_dict,False)
        #return (my_dict,True)
        result={}
        for mConstraint in self.network.constraints:
            counter={}
            for i in range(50):
                counter[i]=0
            if not mConstraint.isConsistent():
                return (result,False)
            for var in mConstraint.vars:
                if not var.isAssigned():
                    for value in var.getValues():
                        counter[value]+=1
            for value in counter.keys():
                if counter[value]==1:
                    for var in mConstraint.vars:
                        if not var.isAssigned():
                            if value in var.getValues():
                                self.trail.push(var)
                                var.assignValue(value)
                                result[var]=value
        return (result,True)



    """
         Optional TODO: Implement your own advanced Constraint Propagation

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
     """
    def getTournCC ( self ):
        return False

    # ==================================================================
    # Variable Selectors
    # ==================================================================

    # Basic variable selector, returns first unassigned variable
    def getfirstUnassignedVariable ( self ):
        for v in self.network.variables:
            if not v.isAssigned():
                return v

        # Everything is assigned
        return None

    """
        Part 1 TODO: Implement the Minimum Remaining Value Heuristic

        Return: The unassigned variable with the smallest domain
    """
    def getMRV ( self ):
        var=None
        num_domain=50
        for v in self.network.variables:
            if not v.isAssigned():
                if v.size()==0:
                    return v
                if v.size()<num_domain:
                    num_domain=v.size()
                    var=v
        return var

    """
        Part 2 TODO: Implement the Degree Heuristic

        Return: The unassigned variable with the most unassigned neighbors
    """
    def getDegree ( self ):
        my_dict={}
        for v in self.network.variables:
            num_of_unas_neighbors=0
            if not v.isAssigned():
                neighbors=self.network.getNeighborsOfVariable(v)
                for neighbor in neighbors:
                    if not neighbor.isAssigned():
                        num_of_unas_neighbors+=1
                my_dict[v]=num_of_unas_neighbors
        if my_dict:
            var_order=sorted(my_dict.keys(),key=lambda k:my_dict[k])
            return var_order[-1]
        return None


    """
        Part 2 TODO: Implement the Minimum Remaining Value Heuristic
                       with Degree Heuristic as a Tie Breaker

        Return: The unassigned variable with the smallest domain and affecting the  most unassigned neighbors.
                If there are multiple variables that have the same smallest domain with the same number of unassigned neighbors, add them to the list of Variables.
                If there is only one variable, return the list of size 1 containing that variable.
    """
    def MRVwithTieBreaker ( self ):
        one_of_smallest_domain_var=self.getMRV()
        if not one_of_smallest_domain_var:
            return []
        domain_size=one_of_smallest_domain_var.size()
        if domain_size==0:return []
        list_of_smallest=[]
        for v in self.network.variables:
            if (not v.isAssigned()) and v.size()==domain_size:
                list_of_smallest.append(v)
        if len(list_of_smallest)==1:
            return list_of_smallest
        my_dict={}
        for var in list_of_smallest:
            num_of_constraints=0
            neighbors=self.network.getNeighborsOfVariable(var)
            for neighbor in neighbors:
                if not neighbor.isAssigned():
                    num_of_constraints+=1
            my_dict[var]=num_of_constraints
        result=[]
        var_order=sorted(my_dict.keys(),key=lambda k:my_dict[k])
        var_order=var_order[::-1]
        result.append(var_order[0])
        if len(var_order)>1:
            for v in var_order[1:]:
                if my_dict[v]==my_dict[var_order[0]]:
                    result.append(v)
        return result


    """
         Optional TODO: Implement your own advanced Variable Heuristic

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
     """
    def getTournVar ( self ):
        return None

    # ==================================================================
    # Value Selectors
    # ==================================================================

    # Default Value Ordering
    def getValuesInOrder ( self, v ):
        values = v.domain.values
        return sorted( values )

    """
        Part 1 TODO: Implement the Least Constraining Value Heuristic

        The Least constraining value is the one that will knock the least
        values out of it's neighbors domain.

        Return: A list of v's domain sorted by the LCV heuristic
                The LCV is first and the MCV is last
    """
    def getValuesLCVOrder ( self, v ):
        v_domain=v.getValues()
        dic={}
        for value in v_domain:
            dic[value]=0
        neighbors=self.network.getNeighborsOfVariable(v)
        for value in v_domain:
            for neighbor in neighbors:
                if not neighbor.isAssigned():
                    if value in neighbor.getValues():
                        dic[value]+=1
        v_valueorder=sorted(v_domain, key=lambda k:dic[k])
        return v_valueorder


    """
         Optional TODO: Implement your own advanced Value Heuristic

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
     """
    def getTournVal ( self, v ):
        return None

    # ==================================================================
    # Engine Functions
    # ==================================================================

    def solve ( self ):
        if self.hassolution:
            return

        # Variable Selection   Only select unassigned variable, if all of variables are assigned, v==None
        v = self.selectNextVariable()

        # check if the assigment is complete
        if ( v == None ):
            for var in self.network.variables:

                # If all variables haven't been assigned   How does this happen?
                if not var.isAssigned():
                    print ( "Error" )

            # Success   After check
            self.hassolution = True
            return

        # Attempt to assign a value     So, v here must be an unassigned variable   What about its domain? Is it propagated?
        for i in self.getNextValues( v ):

            # Store place in trail and push variable's state on trail
            self.trail.placeTrailMarker()
            self.trail.push( v )

            # Assign the value
            v.assignValue( i )

            # Propagate constraints, check consistency, recurse  ? I think from here it checkes consistency and propagate, so v's domain must be reduced due to this previously.
            if self.checkConsistency():
                self.solve()

            # If this assignment succeeded, return
            if self.hassolution:
                return

            # Otherwise backtrack
            self.trail.undo()

    def checkConsistency ( self ):
        if self.cChecks == "forwardChecking":
            return self.forwardChecking()[1]

        if self.cChecks == "norvigCheck":
            return self.norvigCheck()[1]

        if self.cChecks == "tournCC":
            return self.getTournCC()

        else:
            return self.assignmentsCheck()

    def selectNextVariable ( self ):
        if self.varHeuristics == "MinimumRemainingValue":
            return self.getMRV()

        if self.varHeuristics == "Degree":
            return self.getDegree()

        if self.varHeuristics == "MRVwithTieBreaker":
            return self.MRVwithTieBreaker()[0]

        if self.varHeuristics == "tournVar":
            return self.getTournVar()

        else:
            return self.getfirstUnassignedVariable()

    def getNextValues ( self, v ):
        if self.valHeuristics == "LeastConstrainingValue":
            return self.getValuesLCVOrder( v )

        if self.valHeuristics == "tournVal":
            return self.getTournVal( v )

        else:
            return self.getValuesInOrder( v )

    def getSolution ( self ):
        return self.network.toSudokuBoard(self.gameboard.p, self.gameboard.q)
