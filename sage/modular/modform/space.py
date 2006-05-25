"""
Generic spaces of modular forms
"""

#########################################################################
#       Copyright (C) 2004--2006 William Stein <wstein@ucsd.edu>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#                  http://www.gnu.org/licenses/
#########################################################################

from sage.structure.all import Sequence

import sage.modular.hecke.all as hecke
import sage.modular.congroup as congroup
import sage.modular.dirichlet as dirichlet
import sage.rings.all as rings

import defaults
import element
import hecke_operator_on_qexp
import submodule

class ModularFormsSpace(hecke.HeckeModule_generic):
    """
    A generic space of modular forms.
    """
    def __init__(self, group, weight, character, base_ring):
        print "MODULAR FORMS ARE UNDER DEVELOPMENT"
        print "DO *NOT* USE"
        if not isinstance(group, congroup.CongruenceSubgroup):
            raise TypeError, "group (=%s) must be a congruence subroup"%group
        weight = int(weight)
        #if not isinstance(weight, int):
        #    raise TypeError, "weight must be an int"
        if not ((character is None) or isinstance(character, dirichlet.DirichletCharacter)):
            raise TypeError, "character must be a Dirichlet character"
        if not isinstance(base_ring, rings.Ring):
            raise TypeError, "base_ring must be a ring"
        self.__weight, self.__group, self.__character, self.__base_ring = \
                      weight, group, character, base_ring
        hecke.HeckeModule_generic.__init__(self, base_ring, group.level())

    def prec(self, new_prec=None):
        return self.ambient().prec(new_prec)

    def set_precision(self, new_prec):
        self.ambient().set_precision(new_prec)

    def change_ring(self):
        raise NotImplementedError

    def weight(self):
        return self.__weight

    def group(self):
        return self.__group

    def character(self):
        return self.__character

    def base_ring(self):
        return self.__base_ring
    
    def has_character(self):
        return self.character() != None
    
    def is_ambient(self):
        raise NotImplementedError

    def __normalize_prec(self, prec):
        if prec is None:
            prec = self.prec()
        else:
            prec = rings.Integer(prec)
        if prec < 0:
            raise ValueError, "prec (=%s) must be at least 0"%prec
        return prec

    def echelon_form(self):
        r"""
        Return a space of modular forms isomorphic to self but
        with basis of $q$-expansions in reduced echelon form.

        This is useful, e.g., since the default basis for ambient
        spaces is not in echelon form, since it's the space of
        cusp forms in echelon form followed by the Eisenstein
        series in echelon form. 

        EXAMPLES:
        We first illustrate two ambient spaces and their echelon forms.
        
            sage: M = ModularForms(11)
            sage: M.basis()
            [
            q - 2*q^2 - q^3 + 2*q^4 + q^5 + O(q^6),
            1 + 12/5*q + 36/5*q^2 + 48/5*q^3 + 84/5*q^4 + 72/5*q^5 + O(q^6)
            ]
            sage: M.echelon_form().basis()
            [
            1 + 12*q^2 + 12*q^3 + 12*q^4 + 12*q^5 + O(q^6),
            q - 2*q^2 - q^3 + 2*q^4 + q^5 + O(q^6)
            ]

            sage: M = ModularForms(Gamma1(6),4)
            sage: M.basis()
            [
            q - 2*q^2 - 3*q^3 + 4*q^4 + 6*q^5 + O(q^6),
            1 + O(q^6),
            q + 126*q^5 + O(q^6),
            q^2 + O(q^6),
            q^3 + O(q^6)
            ]
            sage: M.echelon_form().basis()
            [
            1 + O(q^6),
            q + 126*q^5 + O(q^6),
            q^2 + O(q^6),
            q^3 + O(q^6),
            q^4 - 30*q^5 + O(q^6)
            ]

        We create a space with a funny basis then compute the corresponding
        echelon form.
            sage: M = ModularForms(11,4)
            sage: M.basis()
            [
            q + 3*q^3 - 6*q^4 - 7*q^5 + O(q^6),
            q^2 - 4*q^3 + 2*q^4 + 8*q^5 + O(q^6),
            1 + O(q^6),
            q + 9*q^2 + 28*q^3 + 73*q^4 + 126*q^5 + O(q^6)
            ]
            sage: F = M.span_of_basis([M.0 + 1/3*M.1, M.2 + M.3]); F.basis()
            [
            q + 1/3*q^2 + 5/3*q^3 - 16/3*q^4 - 13/3*q^5 + O(q^6),
            1 + q + 9*q^2 + 28*q^3 + 73*q^4 + 126*q^5 + O(q^6)
            ]
            sage: E = F.echelon_form(); E.basis()
            [
            1 + 26/3*q^2 + 79/3*q^3 + 235/3*q^4 + 391/3*q^5 + O(q^6),
            q + 1/3*q^2 + 5/3*q^3 - 16/3*q^4 - 13/3*q^5 + O(q^6)
            ]
        """
        try:
            return self.__echelon_form
        except AttributeError:
            E = self.span_of_basis(self.echelon_basis())
            self.__echelon_form = E
            return E

    def echelon_basis(self):
        try:
            return self.__echelon_basis
        except AttributeError:
            F = self.free_module()
            W = self._q_expansion_module()
            pr = W.degree()
            B = self.q_echelon_basis(pr)
            E = [self(F.linear_combination_of_basis(W.coordinates(f.padded_list(pr)))) \
                              for f in B]
            E = Sequence(E, cr=True, immutable=True)
            self.__echelon_basis = E
            return E

    def integral_basis(self):
        try:
            return self.__integral_basis
        except AttributeError:
            W = self._q_expansion_module()
            pr = W.degree()
            B = self.q_integral_basis(pr)
            I = [self(W.coordinates(f.padded_list(pr))) for f in B]
            I = Sequence(I, cr=True, immutable=True)
            self.__integral_basis = I
            return I

    def _q_expansion_module(self, prec=None):
        try:
            return self.__q_expansion_module
        except AttributeError:
            pass
        if prec is None:
            prec = int(1.2*self.dimension()) + 2
        C = self.q_expansion_basis(prec)
        V = self.base_ring()**prec
        try:
            W = V.span_of_basis([f.padded_list(prec) for f in C])
        except AttributeError:
            return self._q_expansion_module(self, 2*prec)
        self.__q_expansion_module = W
        return W
        
    def q_expansion_basis(self, prec=None):
        """
        The number of q-expansions returned equals the dimension.

        INPUT:
            prec -- integer (>=0) or None

        EXAMPLES:
            sage: S = ModularForms(11,2).cuspidal_submodule()
            sage: S.q_expansion_basis(5)
            [
            q - 2*q^2 - q^3 + 2*q^4 + O(q^5)
            ]
            sage: S = ModularForms(1,24).cuspidal_submodule()
            sage: S.q_expansion_basis(5)
            [
            q + 195660*q^3 + 12080128*q^4 + O(q^5),
            q^2 - 48*q^3 + 1080*q^4 + O(q^5)
            ]
        """
        prec = self.__normalize_prec(prec)
        if prec == 0:
            z = self._q_expansion_ring()(0,prec)
            return Sequence([z]*int(self.dimension()), cr=True)
        try:
            current_prec, B = self.__q_expansion_basis
        except AttributeError:
            current_prec, B = -1, Sequence([], cr=True)
        if current_prec == prec:
            return B
        elif current_prec > prec:
            return Sequence([f.add_bigoh(prec) for f in B], cr=True)
        B = self._compute_q_expansion_basis(prec)
        z = self._q_expansion_ring()(0,prec)
        B = B + [z]*(self.dimension() - len(B))
        B = Sequence(B, immutable=True, cr=True)
        self.__q_expansion_basis = (prec, B)
        return B

    def _compute_q_expansion_basis(self, prec):
        raise NotImplementedError

    def q_echelon_basis(self, prec=None):
        r"""
        Return the echelon form of the basis of $q$-expansions of self
        up to precision prec.

        The $q$-expansions are power series (not actual modular forms).
        The number of $q$-expansions returned equals the dimension.
        """
        prec = self.__normalize_prec(prec)
        if prec == 0:
            z = self._q_expansion_ring()(0,0)
            return Sequence([z]*int(self.dimension()), cr=True)
        try:
            current_prec, B = self.__q_echelon_basis
        except AttributeError:
            current_prec, B = -1, []
        if current_prec == prec:
            return B
        elif current_prec > prec:
            return Sequence([f.add_bigoh(prec) for f in B], cr=True)
        
        B = self.q_expansion_basis(prec)
        R = self.base_ring()
        A = R**prec
        gens = [f.padded_list(prec) for f in B]
        C = A.span(gens)
        
        T = self._q_expansion_ring()
        S = [T(f.list(), prec) for f in C.basis()]
        for _ in range(self.dimension() - len(S)):
            S.append(T(0,prec))
        S = Sequence(S, immutable=True, cr=True)
        self.__q_echelon_basis = (prec, S)
        return S
        
        

    def q_integral_basis(self, prec=None):
        r"""
        Return a $\Z$-reduced echelon basis of $q$-expansions for self.

        The $q$-expansions are power series with coefficients in $\Z$;
        they are \emph{not} actual modular forms.

        The base ring of self must be $\Q$.  The number of $q$-expansions
        returned equals the dimension.
                
        EXAMPLES:
            sage: S = CuspForms(11,2)
            sage: S.q_integral_basis(5)
            [
            q - 2*q^2 - q^3 + 2*q^4 + O(q^5)
            ]
        """
        if not self.base_ring() == rings.QQ:
            raise TypeError, "the base ring must be Q"
        prec = self.__normalize_prec(prec)
        R = rings.PowerSeriesRing(rings.ZZ, name=defaults.DEFAULT_VARIABLE)
        if prec == 0:
            z = R(0,prec)
            return Sequence([z]*int(self.dimension()), cr=True)
        try:
            current_prec, B = self.__q_integral_basis
        except AttributeError:
            current_prec, B = -1, Sequence([], cr=True, immutable=True)
            
        if current_prec == prec:
            return B
        elif current_prec > prec:
            return Sequence([f.add_bigoh(prec) for f in B], cr=True)
        
        B = self.q_expansion_basis(prec)

        # It's over Q; we just need to intersect it with ZZ^n.
        A = rings.ZZ**prec
        zero = rings.ZZ(0)
        gens = [f.padded_list(prec) for f in B]        
        C = A.span(gens)
        D = C.saturation()
        S = [R(f.list(),prec) for f in D.basis()]
        for _ in range(self.dimension() - len(S)):
            S.append(R(0,prec))
        S = Sequence(S, immutable=True, cr=True)
        self.__q_integral_basis = (prec, S)
        return S

    def _q_expansion_ring(self):
        try:
            return self.__q_expansion_ring
        except AttributeError:
            R = rings.PowerSeriesRing(self.base_ring(), name=defaults.DEFAULT_VARIABLE)
            self.__q_expansion_ring = R
            return R

    def _q_expansion_zero(self):
        try:
            return self.__q_expansion_zero
        except AttributeError:
            f = self._q_expansion_ring()(0)
            self.__q_expansion_zero = f
            return f

    def _q_expansion(self, element, prec):
        return self.ambient_module()._q_expansion(element, prec)

    def __add__(self, right):
        if self.ambient_space() != right.ambient_space():
            raise ArithmeticError, ("Intersection of %s and %s not defined because they " + \
                                    "do not lie in a common ambient space.")%\
                                   (self, right)
        if self.is_ambient(): return self
        if right.is_ambient(): return right
        V = self.vector_space() + right.vector_space()
        return ModularFormsSubmodule(self.ambient_space(), V)
    

    def __and__(self, right):
        return self.intersect(right)

    def _has_natural_inclusion_map_to(self, right):
        """
        Return true if there is a natural inclusion
        map from modular forms in self to modular forms
        in right.

        INPUT:
            self, right -- spaces of modular forms
        """
        if not right.group().is_subgroup(self.group()):
            return False
        if right.character() is None:
            # It's the full Gamma_1(N).
            return True
        e = self.character()
        f = right.character()
        return f.parent()(e) == f
    
    def __call__(self, x, check=True):
        if isinstance(x, element.ModularFormElement):
            if x.parent() is self:
                return x
            
            if not check:
                f = x.copy()
                f.set_parent(self)
                return f

            try:
                if x.parent()._has_natural_inclusion_map_to(self):
                    W = self._q_expansion_module()
                    return self(x.q_expansion(W.degree()))
            except NotImplementedError:
                pass
            raise TypeError, "unable to coerce x (= %s) into %s"%(x, self)
        
        elif rings.is_PowerSeries(x):
            W = self._q_expansion_module()
            if W.degree() <= x.prec():
                x = W.coordinates(x.padded_list(W.degree()))
                x = self.free_module().linear_combination_of_basis(x)
            else:
                raise TypeError, "q-expansion needed to at least precision %s"%W.degree()
        if check:
            x = self.free_module()(x)
        return element.ModularFormElement(self, x)
    
    def __cmp__(self, x):
        if not isinstance(x, ModularFormsSpace):
            return -1
        if self.is_ambient() or x.is_ambient(): 
            if not (self.is_ambient() and x.is_ambient()): return -1
            if (self.__group, self.__weight, self.__character, self.__base_ring) == \
               (x.__group, x.__weight, x.__character, x.__base_ring):
                return 0
            else:
                return -1
        if self.vector_space() != x.vector_space():
            return -1
        return 0
    
    def __contains__(self, x):
        """
        True if x is an element or submodule of self.
        """
        if self.is_ambient() and x.is_ambient():
            return self.key() == x.key()
        raise NotImplementedError
    
    def __create_newspace(self, basis, level, t, is_cuspidal):
        V = self.vector_space().submodule(basis, check=False)
        S = ModularForms(self.ambient_space(), V)
        S.__newspace_params = {'level':level, 't':t}
        S.__is_cuspidal = is_cuspidal
        S.__is_eisenstein = not is_cuspidal
        return S
    
    def __newspace_bases(self):
        if hasattr(self, "__newspace_bases_list"):
            return self.__newspace_bases_list
        assert self.is_ambient()
        V = self.vector_space()
        eps, k, N = self.__character, self.__weight, self.__level
        # First the cuspidal new spaces.
        m = eps.conductor()
        levels = [M for M in arith.divisors(N) if M%m==0]
        levels.reverse()
        B = []; i = 0
        for M in levels:
            n = dims.dimension_new_cusp_forms(eps.restrict(M), k)
            for t in arith.divisors(N/M):
                basis = [V.gen(i+j) for j in range(n)]
                if len(basis) > 0:
                    B.append((M, t, True, basis))
                i += n
        # Now the Eisenstein series
        #x = [0 for _ in range(len(levels))]
        x = {}
        for E in self.eisenstein_series():  # count number of e.s. of each level
            Mt = (E.new_level(), E.t())
            if not x.has_key(Mt):
                x[Mt] = 1
            else:
                x[Mt] += 1
        k = x.keys()
        k.sort()
        k.reverse()
        for M, t in k:
            n = x[(M,t)]
            B.append((M, t, False, [V.gen(i+j) for j in range(n)]))
            i += n
        self.__newspace_bases_list = B
        return self.__newspace_bases_list

    def span_of_basis(self, B):
        W = self._q_expansion_module()
        F = self.free_module()        
        prec = W.degree()
        C = [F.linear_combination_of_basis(W.coordinates(f.padded_list(prec))) for f in B]
        S = F.span_of_basis(C)
        return submodule.ModularFormsSubmoduleWithBasis(self.ambient(), S)
    
    def span(self, B):
        W = self._q_expansion_module()
        F = self.free_module()
        prec = W.degree()
        C = [F.linear_combination_of_basis(W.coordinates(f.padded_list(prec))) for f in B]
        S = F.span(C)
        return submodule.ModularFormsSubmoduleWithBasis(self.ambient(), S)

    def __submodule_from_subset_of_basis(self, x):
        V = self.vector_space()
        return V.submodule([V.gen(i) for i in x], check=False)
    
    def _compute_hecke_matrix_prime(self, p, prec=None):
        """
        EXAMPLES:
            sage: M = ModularForms(11,2)
            sage: M2 = M.span([M.0 + M.1])
            sage: M2.hecke_matrix(2)
               should raise arithmetic error since not invariant.
        """
        if prec is None:
            # Initial guess -- will increase if need be.
            prec = p*self.dimension() + 1
        try:
            cur, _ = self.__q_expansion_basis
        except AttributeError:
            pass
        else:
            if prec < cur:
                prec = cur
        B = self.q_expansion_basis(prec)
        eps = self.character()
        if eps is None:
            raise NotImplementedError
        try:
            return hecke_operator_on_qexp.hecke_operator_on_basis(B, p,
                       self.weight(), eps, already_echelonized=False)
        except ArithmeticError:
            # Double the precision.
            return self._compute_hecke_matrix_prime(p, prec = 2*prec+1)
        
    
    def _compute_hecke_matrix(self, n):
        if hasattr(self, '_compute_q_expansion_basis'):
            return hecke.HeckeModule_generic._compute_hecke_matrix(self, n)
        else:
            return hecke.HeckeSubmodule._compute_hecke_matrix(self, n)

    def basis(self):
        try:
            return self.__basis
        except AttributeError:
            self.__basis = Sequence([element.ModularFormElement(self, x) for \
                                  x in self.free_module().basis()], immutable=True,
                                    cr = True)
        return self.__basis

    def gen(self, n):
        return self.basis()[n]

    def gens(self):
        return self.basis()
    
    def sturm_bound(self, M=None):
        r"""
        For a space M of modular forms, this function returns an integer B
        such that two modular forms in either self or M are equal if and only
        if their q-expansions are equal to precision B.  If M is none, then
        M is set equal to self.

        NOTES:
        Reference for the Sturm bound that we use in the definition of
        of this function:
        
         J. Sturm, On the congruence of modular forms, 
              Number theory (New York, 1984--1985), Springer,
              Berlin, 1987, pp.~275--280.
        
        Useful Remark:
        
            Kevin Buzzard pointed out to me (William Stein) in Fall
            2002 that the above bound is fine for Gamma1 with
            character, as one sees by taking a power of $f$.  More
            precisely, if $f\con 0\pmod{p}$ for first $s$
            coefficients, then $f^r = 0 \pmod{p}$ for first $s r$
            coefficents.  Since the weight of $f^r$ is $r
            \text{weight}(f)$, it follows that if $s \geq $ the sturm
            bound for $\Gamma_0$ at weight(f), then $f^r$ has
            valuation large enough to be forced to be $0$ at $r\cdot$
            weight(f) by Sturm bound (which is valid if we choose $r$
            right).  Thus $f \con 0 \pmod{p}$.  Conclusion: For
            $\Gamma_1$ with fixed character, the Sturm bound is
            \emph{exactly} the same as for $\Gamma_0$.  A key point is
            that we are finding $\Z[\eps]$ generators for the Hecke
            algebra here, not $\Z$-generators.  So if one wants
            generators for the Hecke algebra over $\Z$, this bound is
            wrong.
        
            This bound works over any base, even a finite field.
            There might be much better bounds over $\Q$, or for
            comparing two eigenforms.
        """
        if M != None:
            raise NotImplementedError
        if self.__sturm_bound == None:
            # the +1 below is because O(q^prec) has precision prec.
            self.__sturm_bound = int(\
                math.ceil(self.weight()*dims.idxG0(self.level())/12.0) + 1)
        return self.__sturm_bound
    
    def character(self):
        return self.__character
    
    def cuspidal_submodule(self):
        if self.__is_cuspidal == True:
            return self
        if self.__cuspidal_submodule != None:
            return self.__cuspidal_submodule
        if self.is_ambient():
            # By definition the cuspidal submodule of the ambient space
            # is spanned by the first n standard basis vectors, where
            # n is the dimension of the cuspidal submodule.
            n = self.__ambient_cusp_dimension()
            W = self.__submodule_from_subset_of_basis(range(n))
            S = ModularForms(self, W)
            S.__is_cuspidal = True
            S.__is_eisenstein = (n==0)
            self.__cuspidal_submodule = S
            return S
        C = self.ambient_space().cuspidal_submodule()
        S = self.intersect(C)
        if S.dimension() < self.dimension():
            self.__is_cuspidal = False
            self.__cuspidal_submodule = S
        else:
            assert S.dimension() == self.dimension()
            self.__is_cuspidal = True
        S.__is_eisenstein = (S.dimension()==0)

    def cuspidal_subspace(self):
        """
        Synonym for cuspidal_submodule.
        """
        return self.cuspidal_submodule()

    def new_subspace(self, p=None):
        """
        Synonym for new_submodule.
        """
        return self.new_submodule(p)

    def eisenstein_subspace(self):
        """
        Synonym for eisenstein_submodule.
        """
        return self.eisenstein_submodule()
        
    def decomposition(self):
        """

        This function returns a list of submodules $V(f_i,t)$
        corresponding to newforms $f_i$ of some level dividing the
        level of self, such that the direct sum of the submodules
        equals self, if possible.  The space $V(f_i,t)$ is the image
        under $g(q)$ maps to $g(q^t)$ of the intersection with
        $R[[q]]$ of the space spanned by the conjugates of $f_i$,
        where $R$ is the base ring of self.

        """
        raise NotImplementedError        

    def newspaces(self):
        r"""
        This function returns a list of submodules $S(M,t)$ and
        $E(M,t)$, corresponding to levels $M$ dividing $N$ and integers $t$
        dividing $N/M$, such that self is the direct sum of these
        spaces, if possible.  Here $S(M,t)$ is by definition
        the image under $f(q) \mapsto f(q^t)$ of the new submodule of
        cusp forms of level $M$, and similarly $E(M,t)$ is the image of
        Eisenstein series.

        Notes: (1) the submodules $S(M,t)$ need not be stable under
        Hecke operators of index dividing $N/M$.  (2) Since self can
        be an arbitrary submodule, there's no guarantee any $S(M,t)$ or
        $E(M,t)$ is in self, so the return list could be empty.
        """
        V = self.embedded_submodule()
        return [self.__create_newspace(basis=B,level=M,t=t,is_cuspidal=is_cuspidal) \
                for M, t, is_cuspidal, B in self.ambient_space().__newspace_bases() \
                if V.contains_each(B)]

    
    def eisenstein_submodule(self):
        if self.__is_eisenstein == True:
            return self
        if self.__eisenstein_submodule != None:
            return self.__eisenstein_submodule
        if self.is_ambient():
            # By definition the eisenstein submodule of the ambient space
            # is spanned by the n+1 through n+d standard basis vectors, where
            # n is the dimension of the cuspidal submodule and d
            # is the dimension of the eisenstein submodule (i.e., the
            # number of eisenstein series).
            n = self.__ambient_cusp_dimension()
            d = self.__ambient_eis_dimension()
            W = self.__submodule_from_subset_of_basis(range(n,n+d))
            E = ModularForms(self, W)
            E.__is_eisenstein = True
            E.__is_cuspidal = (d==0)
            self.__eisenstein_submodule = E
            return E
        A = self.ambient_space().eisenstein_submodule()
        E = self.intersect(A)
        if E.dimension() < self.dimension():
            self.__is_eisenstein = False
            self.__eisenstein_submodule = E
        else:
            assert E.dimension() == self.dimension()
            self.__is_eisenstein = True
        E.__is_cuspidal = (E.dimension()==0)
        
    def embedded_submodule(self):
        if self.is_ambient():
            return self.vector_space()
        return self.__embedded_submodule

    def intersect(self, right):
        if self.ambient_space() != right.ambient_space():
            raise ArithmeticError, "Intersection of %s and %s not defined."%\
                                   (self, right)
        V = self.embedded_submodule().intersect(right.embedded_submodule())
        return ModularForms(self.ambient_space(),V)
    
    def is_ambient(self):
        return self.__ambient == None
    
    def key(self):
        if self.is_ambient():
            return self.__key
        return self.__ambient
    
    def level(self):
        return self.group().level()
    
    def modular_symbols(self, sign=0):
        raise NotImplementedError

