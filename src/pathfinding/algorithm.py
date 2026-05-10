# A* Search Algorithm’s formula calculates
# the cost of reaching a particular node. 

# Formula: f(n)=g(n)+h(n)
 # f(n) is the estimated total cost from the start node
    # to the end goal via node n.
 # g(n) is the actual cost from the start node to node n.
 # h(n) is the heuristic cost (estimated cost) from node n
    # to end node.

# // A* Search Algorithm
# 1.  Initialize the open list
# 2.  Initialize the closed list
#     put the starting node on the open 
#     list (you can leave its f at zero)
# 3.  while the open list is not empty
#     a) find the node with the least f on 
#        the open list, call it "q"
#     b) pop q off the open list
  
#     c) generate q's 8 successors and set their 
#        parents to q
   
#     d) for each successor
#         i) if successor is the goal, stop search
        
#         ii) else, compute both g and h for successor
#           successor.g = q.g + distance between 
#                               successor and q
#           successor.h = distance from goal to 
#           successor (This can be done using many 
#           ways, we will discuss three heuristics- 
#           Manhattan, Diagonal and Euclidean 
#           Heuristics)
          
#           successor.f = successor.g + successor.h
#         iii) if a node with the same position as 
#             successor is in the OPEN list which has a 
#            lower f than successor, skip this successor
#         iV) if a node with the same position as 
#             successor  is in the CLOSED list which has
#             a lower f than successor, skip this successor
#             otherwise, add  the node to the open list
#      end (for loop)
  
#     e) push q on the closed list
#     end (while loop)


from ..map.network import Network, Hub
from typing import Any


ZONE_COST = {
    "priority": 0,
    "normal": 1,
    "restricted": 2,
}


def a_star(net: Network) -> set[Hub]:
    '''A* Search Algorithm'''
    assert net.start is not None
    visited: set[Hub] = set()      # closed list
    queue: list[Hub] = [net.start] # open list

    while queue:
        if len(queue) > 1:
            current = queue.pop()
            q = best_neighbour(current)
        current: Hub = queue.pop()
        if current is net.end:
            path = get_path(visited)
            return path
        


def best_neighbour(current: Hub) -> Hub:
    '''Use zone_cost to find best neighbours'''
    ...


def get_path(visited: set) -> set[Hub]:
    ...


def print_statistic() -> None:
    '''Print statistics for efficiency tracking'''
    ...
