/// SimplicialComplex.h
/// Shaun Harker
/// MIT LICENSE
/// 2018-03-09

/*

An implementation of a simplicial complex which indices the simplices naively requires
O(nd) space to store the indexing scheme. This scheme allows for O(d^2) computation of boundaries;
if the boundary matrix is computed once and stored then for O(nd) memory an output sensitive linear
time boundary algorithm is possible.
To enable a coboundary computation the transpose of the boundary matrix, requiring again O(nd) space
must be stored.

Altogether, this means it would take $O(nd^2)$ time to prepare a simplicial complex structure which 
occupies $O(nd)$ space.

Can we do better?

An idea is to assign to each vertex some "hash_value" and to each simplex the sum of the hash values of each vertex.
Our goal is then to ensure that any two simplices in the complex have distinct hashes, so we may use these hash values
as unique identifiers.

We would then have a hash table that for each hash_value gave us some vertex in the simplex. (perhaps order vertices and ask that it is maximal)
The vertex is probably conveniently given as the hash_value, i.e. a 0-dim simplex.

Then the boundary computation can be performed as follows.

```
def bd(s_hash):
    """
    input: s_hash, which is the sum of the hash_values of the vertices of some simplex
    result = []
    t_hash = s_hash
    while t_hash > 0:
        v_hash = vertex(t_hash)
        t_hash -= v_hash
        result.append(s_hash - v_hash)
    return result
```

The space requirement for this structure is $O(n)$.

How hard is it to construct the O(n) data structure?

```
def add_simplex(s):
    """
    here s is a list of vertex indices
    """
    vertex[sum(s)]=max(s)
```

```
def add_closed_simplex(s):
    """
    here s is a list of vertex indices
    """
    stack = []
    n = len(s)
    stack.append( (sum(s), 2**n - 1) )
    while stack:
        (t, code) = stack.pop()
        if t in vertex:
            continue
        vertex[t] = s[maxbit[code]]
        for k in bits(code):  # loop through 1's in 2**n - 1, presumably some bit twiddle magic
            stack.append((t - s[k], code - 2**k))
```

Is this a practical thing to spend time on? For d > 12 the size of a single closed simplex starts getting very big.

So at best we save an order of magnitude of speed outside the construction phase.

The construction phase going from $O(nd^2)$ to $O(n)$ of course is nothing to sneeze at.

It is an unsolved problem how to assign values to vertices to get uniqueness. Randomness is likely to work
with 64-bit keys as long as we have fewer than 4E9 simplices. Can we do better:

1. Get a guarantee that there are no collisions
2. Find a way to choose vertex values such that the hashes in $Z_M$ for some M not much bigger than n are distinct?

Accomplishing (2) would be interesting since it would allow us to use an array to store a vertex for each simplex
without having too much wasted space. 

What we have is a matrix equation

Ax = y

and we want to find integer solution for x such that the entries of y are distinct and ||y||_{\infty} is minimized.


consider the following start:
* ----- * ----- * ----- * ----- *
a   9   b  10   c   6   d   7   e
1       A       2       B       3

1 + A
2 + A
2 + B
3 + B

case 1. A < B.
Then these values are distinct, BUT
1+A==B or 2+A==B are disallowed.

* ----- * ----- * ----- * ----- *
a   5   b  6   c   9   d   10   e
1       4       2      7       3

case 2. A > B.
A == B + 1 disallowed A == B+2 disallowed A == B+3 disallowed

* ----- * ----- * ----- * ----- *
a   9   b   10  c   6   d   7   e
1       8       2       4       3

* ----- * ----- * ----- * ----- *
a   8   b   10  c   5   d   6   e
1       7       3       2       4

* ----- * ----- * ----- * ----- *
a   4   b   9   c   8   d   7   e
1       3       6       2       5

* ----- *
a   3   b 
1       2

* ----- * ----- *
a   4   b   5   c
1       3       2

* ----- * ----- *
a   5   b   3   c
4       1       2

* ----- * ----- * ----- *
a   4   b   6   c   7   d
3       1       5       2

* ----- * ----- * ----- *
a   7   b   4   c   5   d
6       1       3       2

* ----- * ----- * ----- * ----- *
a   4   b   9   c   8   d   7   e
1       3       6       2       5



1   --3-- 2 --6-- 4 --5-- 1
Suppose we filter simplices according to some ordering of the vertices (i.e. we handle all simplices involving only the first k
vertices, then consider all new vertices that involve vertex k+1, etc)

Let's say we try to assign the vertex the smallest integer we can. How hard is this integer to find?
If we are lazy and don't need the best we can just pick the largest hash seen so far and use that +1. The hope would
be that for random orderings of vertices this results in a reasonably small labelling.


Is there always a perfect hash?

*-----*  *-----*
1  3  2  4  9  5

*-----*  *-----*
1  4  3  2  7  5

*-----*  *-----*
1  5  4  2  8  6

*-----*  *-----*
1  6  5  2  8  6

*-----*  *-----*
1  7  6  2  5  3

no, there isn't. mod 7?

*-----*  *-----*
2  1  6   nope


here is a solution:
*-----*  *-----*
3  1  5  2  6  4

question: modulo N+1, is there a solution?

4 vertices, 4 + 6 + 4 + 1 = 15 nonempty. mod 16.

Remove interior and all faces, keeping only 1 skeleton.

mod 11.

1,2,4,8
3,5,9,6,10,12
4 + 8 = 12 == 1

1,2,4,7 is best way to do it, 10 goes unused.


*/
#pragma once

#include "common.h"

typedef std::vector<Integer> Simplex;

inline std::vector<Simplex>
simplex_boundary(Simplex const& s) {
  //std::cout << "bd ["; for ( auto v : s ) std::cout << v << ", "; std::cout << "] = \n";
  std::vector<Simplex> result;
  if ( s.size() > 1 ) {
    for ( Integer i = 0; i < s.size(); ++ i ) {
      Simplex t = s;
      t.erase(t.begin() + i);
      result.push_back(t);
      //std::cout << "  ["; for ( auto v : t ) std::cout << v << ", "; std::cout << "] + \n";
    }
  }
  return result;
}

/// SimplicialComplex
class SimplicialComplex : public Complex {
public:

  /// SimplicialComplex
  SimplicialComplex ( std::vector<Simplex> const& maximal_simplices );

  /// column
  ///   Apply "callback" method to every element in ith column of
  ///   boundary matrix
  virtual void
  column ( Integer i, std::function<void(Integer)> const& callback) const final;

  /// row
  ///   Apply "callback" method to every element in ith row of
  ///   boundary matrix
  virtual void
  row ( Integer i, std::function<void(Integer)> const& callback) const final;

  /// simplex
  ///   Given a cell index, return the associated Simplex
  Simplex
  simplex ( Integer i ) const;

  /// idx
  ///   Given a simplex object, return the associated cell index.
  ///   If simplex not in complex, return -1.
  Integer
  idx ( Simplex const& s ) const;

private:
  std::unordered_map<Simplex, Integer, pychomp::hash<Simplex>> idx_;
  std::vector<Simplex> simplices_;
  std::vector<Chain> bd_;
  std::vector<Chain> cbd_;
  
  /// add_simplex
  bool
  add_simplex ( Simplex const& s );

  /// add_closed_simplex
  void
  add_closed_simplex ( Simplex const& s );
  
};

inline SimplicialComplex::
SimplicialComplex (std::vector<Simplex> const& max_simplices) {
  //std::cout << "SimplicialComplex " << max_simplices.size() << "\n";
  for ( auto s : max_simplices ) add_closed_simplex ( s );
  Integer N = simplices_.size();
  std::sort(simplices_.begin(), simplices_.end(), []( Simplex const& lhs, Simplex const& rhs ){ return lhs.size() < rhs.size(); });
  idx_.clear();
  for ( Integer i = 0; i < N; ++ i ) idx_[simplices_[i]] = i;
  dim_ = -1;
  bd_.resize(N);
  cbd_.resize(N);
  for ( Integer i = 0; i < N; ++ i ) {
    Simplex const& s = simplices_[i];
    Integer simplex_dim = s.size() - 1;
    // std::cout << "i = " << i << "\n";
    // std::cout << " s =  ["; for ( auto v : s ) std::cout << v << ", "; std::cout << "] + \n";
    // std::cout << " simplex_dim == " << simplex_dim << "\n";
    // std::cout << " dim_ == " << dim_ << "\n";
    if ( simplex_dim > dim_ ) {
      // std::cout << "New dimension\n";
      ++ dim_;
      begin_.push_back(Iterator(i));
      // std::cout << "Pushed " << i << " onto begin_\n";
    }
    Chain c;
    for ( Simplex const& t : simplex_boundary(s) ) c += idx_[t];
    bd_[i] = c;
    //std::cout << "boundary of " << i << " is equal to " << c << "\n";
  }
  begin_.push_back(Iterator(N));
  // std::cout << "Pushed " << N << " onto begin_\n";

  for ( Integer i = 0; i < N; ++ i ) {
    Chain bd = bd_[i];
    for ( Integer j : bd ) {
      cbd_[j] += i;
    }
  }
}

inline Simplex SimplicialComplex::
simplex ( Integer i ) const{
  return simplices_[i];
}

inline Integer SimplicialComplex::
idx ( Simplex const& s ) const {
  auto it = idx_.find(s);
  if ( it == idx_.end() ) return -1;
  return it -> second;
}

inline bool SimplicialComplex::
add_simplex (Simplex const& s) {
  if ( idx(s) == -1 ) {
    idx_[s] = simplices_.size();
    simplices_.push_back(s);
    return true;
  } else {
    return false;
  }
}

inline void SimplicialComplex::
add_closed_simplex (Simplex const& s) {
  std::stack < Simplex > work_stack;
  work_stack.push(s);
  while ( not work_stack.empty() ) {
    auto t = work_stack.top();
    work_stack.pop();
    bool inserted = add_simplex(t);
    if ( inserted ) {
      for ( auto u : simplex_boundary(t) ) {
        work_stack.push(u);
      }
    }
  }
}

inline void SimplicialComplex::
column ( Integer i, std::function<void(Integer)> const& callback ) const { 
  for ( auto x : bd_[i] ) callback(x);
}

inline void SimplicialComplex::
row ( Integer i, std::function<void(Integer)> const& callback ) const {
  for ( auto x : cbd_[i] ) callback(x);
}

/// Python Bindings

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
namespace py = pybind11;

inline void
SimplicialComplexBinding(py::module &m) {
  py::class_<SimplicialComplex, std::shared_ptr<SimplicialComplex>, Complex>(m, "SimplicialComplex")
    .def(py::init<std::vector<Simplex> const&>())
    .def("simplex", &SimplicialComplex::simplex)
    .def("idx", &SimplicialComplex::idx);
}