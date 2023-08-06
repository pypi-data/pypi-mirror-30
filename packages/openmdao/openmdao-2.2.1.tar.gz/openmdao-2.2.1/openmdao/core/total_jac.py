"""
Helper class for total jacobian computation.
"""
from __future__ import print_function, division

from collections import OrderedDict
import numpy as np
from six import iteritems, itervalues

from openmdao.utils.general_utils import ContainsAll


_contains_all = ContainsAll()


class _TotalJacInfo(object):
    """
    Object to manage computation of total derivatives.

    Attributes
    ----------
    comm : MPI.Comm or <FakeComm>
        The global communicator.
    relevant : dict
        Map of absolute var name to vars that are relevant to it.
    fwd : bool
        If True, compute deriv in forward mode, else reverse (adjoint) mode.
    out_meta : dict
        Map of absoute output var name to tuples of the form (indices, distrib).
    owning_ranks : dict
        Map of absolute var name to the MPI process that owns it.
    _idx2name : dict
        Map of row/col index to variable name.  Used only if simul coloring is active.
    idx2local : dict
        Map of row/col index to index within a variable.  Used only if simul coloring is active.
    output_vec : Dict of vectors keyed by vec_name.
        Designated output vectors based on value of fwd.
    simul_coloring : tuple of the form (column_lists, row_map, sparsity) or None
        Contains all data necessary to simultaneously solve for groups of total derivatives.
    has_lin_cons : bool
        If True, this total jacobian contains linear constraints.
    output_list : list of str
        List of names of output variables for this total jacobian.  In fwd mode, outputs
        are responses.  In rev mode, outputs are design variables.
    J : ndarray
        The dense array form of the total jacobian.
    Jfinal : ndarray or dict
        If return_format is 'array', Jfinal is J.  Otherwise it's either a nested dict (if
        return_format is 'dict') or a flat dict (return_format 'flat_dict').
    idx_iter_dict : dict
        A dict containing an entry for each outer iteration of the total jacobian computation.
    """

    def __init__(self, problem, of, wrt, global_names, return_format):
        """
        Initialize object.

        Parameters
        ----------
        problem : <Problem>
            Reference to that Problem object that contains this _TotalJacInfo.
        of : iter of str
            Response names.
        wrt : iter of str
            Design variable names.
        global_names : bool
            If True, names in of and wrt are global names.
        return_format : str
            Indicates the desired return format of the total jacobian. Can have value of
            'array', 'dict', or 'flat_dict'.
        """
        model = problem.model
        self.comm = problem.comm
        self.relevant = model._relevant
        self.fwd = (problem._mode == 'fwd')
        self.owning_ranks = problem.model._owning_rank

        abs2meta = model._var_allprocs_abs2meta

        design_vars = problem.driver._designvars
        responses = problem.driver._responses
        constraints = problem.driver._cons

        vec_doutput = model._vectors['output']
        vec_dresid = model._vectors['residual']

        prom2abs = model._var_allprocs_prom2abs_list['output']

        # Convert of and wrt names from promoted to unpromoted
        # (which is absolute path since we're at the top)
        if wrt is None:
            wrt = old_wrt = list(design_vars)
        else:
            old_wrt = wrt
            if not global_names:
                wrt = [prom2abs[name][0] for name in old_wrt]

        if of is None:
            of = list(problem.driver._objs)
            of.extend(problem.driver._cons)
            old_of = of
        else:
            old_of = of
            if not global_names:
                of = [prom2abs[name][0] for name in old_of]

        if self.fwd:
            self.input_list, self.output_list = wrt, of
            self.input_meta, output_meta = design_vars, responses
            self.input_vec, self.output_vec = vec_dresid, vec_doutput
        else:  # rev
            self.input_list, self.output_list = of, wrt
            self.input_meta, output_meta = responses, design_vars
            self.input_vec, self.output_vec = vec_doutput, vec_dresid

        for name in of:
            if name in constraints and constraints[name]['linear']:
                has_lin_cons = True
                break
        else:
            has_lin_cons = False

        self.has_lin_cons = has_lin_cons

        self.out_meta, out_size = self._create_meta_map(self.output_list, output_meta, abs2meta)
        if not has_lin_cons and problem.driver._simul_coloring_info is not None:
            self.simul_coloring = problem.driver._simul_coloring_info
            self._idx2name, self.idx2local = self._create_idx_maps(self.output_list, output_meta,
                                                                   abs2meta, out_size)
        else:
            self._idx2name = self.idx2local = self.simul_coloring = None

        self.input_idx_map, self.input_loc_idxs, self.idx_iter_dict = \
            self._create_input_idx_map(self.input_list, self.input_meta, has_lin_cons,
                                       model._var_sizes, model._var_allprocs_abs2idx, abs2meta)

        # always allocate a 2D dense array and we can assign views to dict keys later if
        # return format is 'dict' or 'flat_dict'.
        if self.fwd:
            self.J = J = np.zeros((out_size, self.input_loc_idxs.size))
        else:  # rev
            self.J = J = np.zeros((self.input_loc_idxs.size, out_size))

        # for dict type return formats, map var names to views of the Jacobian array.
        if return_format == 'array':
            self.Jfinal = J
        else:
            self.Jfinal = self._get_dict_J(J, wrt, old_wrt, of, old_of,
                                           self.input_meta, self.out_meta, abs2meta, return_format)

    def _get_dict_J(self, J, wrt, oldwrt, of, oldof, input_meta, out_meta, abs2meta, return_format):
        """
        Create a dict or flat-dict jacobian that maps to views in the given 2D array jacobian.

        Parameters
        ----------
        J : ndarray
            Array jacobian.
        wrt : iter of str
            Absolute names of input vars.
        oldwrt : iter of str
            Promoted names of input vars.
        of : iter of str
            Absolute names of output vars.
        oldof : iter of str
            Promoted names of output vars.
        input_meta : dict
            Dict of input voi metadata.
        out_meta : dict
            Dict mapping output name to array jacobian slice, indices, and distrib.
        abs2meta : dict
            Mapping of absolute var name to metadata dict for that var.
        return_format : str
            Indicates the desired form of the returned jacobian.

        Returns
        -------
        dict
            Dict form of the total jacobian that contains views of the ndarray jacobian.
        """
        if self.fwd:
            meta_in, in_size = self._create_meta_map(wrt, input_meta, abs2meta)
            meta_out = out_meta
        else:
            meta_out, in_size = self._create_meta_map(of, input_meta, abs2meta)
            meta_in = out_meta

        Jdict = OrderedDict()
        if return_format == 'dict':
            for i, out in enumerate(of):
                Jdict[oldof[i]] = outer = OrderedDict()
                out_slice = meta_out[out][0]
                for j, inp in enumerate(wrt):
                    outer[oldwrt[j]] = J[out_slice, meta_in[inp][0]]
        elif return_format == 'flat_dict':
            for i, out in enumerate(of):
                out_slice = meta_out[out][0]
                for j, inp in enumerate(wrt):
                    Jdict[oldof[i], oldwrt[j]] = J[out_slice, meta_in[inp][0]]
        else:
            raise ValueError("'%s' is not a valid jacobian return format." % return_format)

        return Jdict

    def _create_input_idx_map(self, names, vois, has_lin_constraints, var_sizes, abs2idx, abs2meta):
        """
        Create a list that maps a global index to a name, col/row range, and other data.

        Parameters
        ----------
        names : iter of str
            Names of the variables making up the rows or columns of the jacobian.
        vois : dict
            Mapping of variable of interest (desvar or response) name to its metadata.
        has_lin_constraints : bool
            If True, there are linear constraints used to compute the total jacobian.
        var_sizes : dict of dict of arrays
            Container for all variable sizes based on vec_name, input/output, and rank.
        abs2idx : dict
            Mapping of absolute var name to index of that var in the list of vars of the same
            type (input or output).
        abs2meta : dict
            Mapping of absolute var name to metadata dict for that var.

        Returns
        -------
        list
            List of (name, rhsname, rel_systems) tuples.
        ndarray
            array of local indices
        dict
            dictionary of iterators.
        """
        idx_map = []
        start = 0
        end = 0
        iproc = self.comm.rank
        owning_ranks = self.owning_ranks
        relevant = self.relevant
        has_par_deriv_color = False

        idx_tups = [None] * len(names)
        loc_idxs = []
        idx_iter_dict = OrderedDict()  # a dict of index iterators

        simul_coloring = self.simul_coloring

        for name in names:
            rhsname = 'linear'
            in_var_meta = abs2meta[name]

            if name in vois:
                # if name is in vois, then it has been declared as either a design var or
                # a constraint or an objective.
                meta = vois[name]
                end += meta['size']

                parallel_deriv_color = meta['parallel_deriv_color']
                matmat = meta['vectorize_derivs']
                cache_lin_sol = meta['cache_linear_solution']

                _check_voi_meta(name, parallel_deriv_color, matmat, simul_coloring)
                if matmat or parallel_deriv_color:
                    rhsname = name

                in_idxs = meta['indices'] if 'indices' in meta else None

                if in_idxs is None:
                    # if the var is not distributed, global_size == local size
                    irange = np.arange(in_var_meta['global_size'], dtype=int)
                else:
                    irange = in_idxs
                    # correct for any negative indices
                    irange[in_idxs < 0] += in_var_meta['global_size']

            else:  # name is not a design var or response  (should only happen during testing)
                end += abs2meta[name]['size']
                irange = np.arange(in_var_meta['global_size'], dtype=int)
                in_idxs = parallel_deriv_color = matmat = None
                cache_lin_sol = False

            in_var_idx = abs2idx[rhsname][name]
            sizes = var_sizes[rhsname]['output']
            gstart = np.sum(sizes[:iproc, in_var_idx])
            gend = gstart + sizes[iproc, in_var_idx]

            if not in_var_meta['distributed']:
                # if the var is not distributed, convert the indices to global.
                # We don't iterate over the full distributed size in this case.
                owner = owning_ranks[name]
                if owner == iproc:
                    irange += gstart
                else:
                    owner_start = np.sum(sizes[:owner, in_var_idx])
                    irange += owner_start

            # all local idxs that correspond to vars from other procs will be -1
            # so each entry of loc_i will either contain a valid local index,
            # indicating we should set the local vector entry to 1.0 before running
            # solve_linear, or it will contain -1, indicating we should not set any
            # value before calling solve_linear.
            loc_i = np.full(irange.shape, -1, dtype=int)
            if gend > gstart:
                loc = np.logical_and(irange >= gstart, irange < gend)
                if in_idxs is None:
                    loc_i[loc] = np.arange(0, gend - gstart, dtype=int)[loc]
                else:
                    loc_i[loc] = irange[loc]

            loc_idxs.append(loc_i)

            if name in relevant:
                rel = relevant[name]['@all'][1]
            else:
                rel = _contains_all

            if parallel_deriv_color:
                has_par_deriv_color = True
                if parallel_deriv_color not in idx_iter_dict:
                    if matmat:
                        it = self.par_deriv_matmat_iter
                    else:
                        it = self.par_deriv_iter
                    idx_iter_dict[parallel_deriv_color] = (parallel_deriv_color, matmat,
                                                           [(start, end)], it)
                else:
                    _, old_matmat, range_list, _ = idx_iter_dict[parallel_deriv_color]
                    if old_matmat != matmat:
                        raise RuntimeError("Mixing of vectorized and non-vectorized derivs in the "
                                           "same parallel color group (%s) is not supported." %
                                           parallel_deriv_color)
                    range_list.append((start, end))
            elif matmat:
                if name not in idx_iter_dict:
                    idx_iter_dict[name] = (parallel_deriv_color, matmat,
                                           [np.arange(start, end, dtype=int)], self.matmat_iter)
                else:
                    raise RuntimeError("Variable name '%s' matches a parallel_deriv_color name." %
                                       name)
            elif not simul_coloring:  # plain old single index iteration
                idx_iter_dict[name] = (parallel_deriv_color, matmat,
                                       np.arange(start, end, dtype=int), self.single_index_iter)

            tup = (name, rhsname, rel, cache_lin_sol)
            idx_map.extend([tup] * (end - start))
            start = end

        if has_par_deriv_color:
            _fix_pdc_lengths(idx_iter_dict)

        if simul_coloring:
            idx_iter_dict['@simul_coloring'] = (False, False, self.simul_coloring,
                                                self.simul_coloring_iter)

        return idx_map, np.hstack(loc_idxs), idx_iter_dict

    def _create_meta_map(self, names, vois, abs2meta):
        """
        Create a dict that maps var name to metadata tuple.

        The tuple has the form (jacobian row/column slice, indices, distrib)

        Parameters
        ----------
        names : iter of str
            Names of the variables making up the rows or columns of the jacobian.
        vois : dict
            Mapping of variable of interest (desvar or response) name to its metadata.
        abs2meta : dict
            Mapping of absolute var name to metadata for that var.

        Returns
        -------
        dict
            Dict of metadata tuples keyed by output name.
        int
            Total number of rows or columns.
        """
        idx_map = {}
        start = 0
        end = 0

        for name in names:
            if name in vois:
                size = vois[name]['size']
                indices = vois[name]['indices']
            else:
                size = abs2meta[name]['size']
                indices = None

            end += size

            idx_map[name] = (slice(start, end), indices, abs2meta[name]['distributed'])
            start = end

        return idx_map, end  # after the loop, end is the total size

    def _create_idx_maps(self, names, vois, abs2meta, size):
        """
        Create a list that maps jacobian row/column index to var name.

        Parameters
        ----------
        names : iter of str
            Names of the variables making up the rows or columns of the jacobian.
        vois : dict
            Mapping of variable of interest (desvar or response) name to its metadata.
        abs2meta : dict
            Mapping of absolute var name to metadata for that var.
        size : int
            Total number of rows/columns.

        Returns
        -------
        list
            List that maps row/col index to variable name.
        ndarray
            Array that maps row/col index to local variable index
        """
        idx2name = [None] * size
        idx2local = np.empty(size, dtype=int)

        start = end = 0
        for name in names:
            if name in vois:
                end += vois[name]['size']
            else:
                end += abs2meta[name]['size']

            idx2name[start:end] = [name] * (end - start)
            idx2local[start:end] = np.arange(0, end - start, dtype=int)
            start = end

        return idx2name, idx2local

    #
    # outer loop iteration functions
    #
    def single_index_iter(self, idxs):
        """
        Iterate over single indices for a single variable.

        Parameters
        ----------
        idxs : iter of int
            Total jacobian row/column indices.

        Yields
        ------
        int
            Current index.
        method
            Input setter method.
        method
            Jac setter method.
        """
        for i in idxs:
            yield i, self.single_input_setter, self.single_jac_setter

    def simul_coloring_iter(self, coloring_info):
        """
        Iterate over index lists for the simul coloring case.

        Parameters
        ----------
        coloring_info : tuple of the form (column_lists, row_map, sparsity)
            Row/column data needed to group colors and associate rows and columns.

        Yields
        ------
        list of int or int
            Current indices or current index.
        method
            Input setter method.
        method
            Jac setter method.
        """
        col_lists = coloring_info[0]

        for color, ilist in enumerate(col_lists):
            if color == 0:  # first outer loop gives all non-colored indices.
                for j in ilist:
                    # do all non-colored indices individually (one linear solve per index)
                    yield j, self.single_input_setter, self.single_jac_setter
            else:
                # yield all indices for a color at once
                # use color as lin sol cache key
                yield ilist, self.simul_coloring_input_setter, self.simul_coloring_jac_setter

    def par_deriv_iter(self, idxs):
        """
        Iterate over index lists for the parallel deriv case.

        Parameters
        ----------
        idxs : iter of int
            Total jacobian row/column indices.

        Yields
        ------
        list of int
            Current indices.
        method
            Input setter method.
        method
            Jac setter method.
        """
        for tup in zip(*idxs):
            yield tup, self.par_deriv_input_setter, self.par_deriv_jac_setter

    def matmat_iter(self, idxs):
        """
        Iterate over index lists for the matrix matrix case.

        Parameters
        ----------
        idxs : ndarray of int
            Total jacobian row/column indices.

        Yields
        ------
        list of int
            Current indices.
        method
            Input setter method.
        method
            Jac setter method.
        """
        for idx_list in idxs:
            yield idx_list, self.matmat_input_setter, self.matmat_jac_setter,

    def par_deriv_matmat_iter(self, idxs):
        """
        Iterate over index lists for the combined parallel deriv matrix matrix case.

        Parameters
        ----------
        idxs : iter of int
            Total jacobian row/column indices.

        Yields
        ------
        list of ndarray of int
            Current indices.
        method
            Input setter method.
        method
            Jac setter method.
        """
        # here, idxs is a list of arrays.  One array in the list for each parallel deriv
        # variable, and the entries in each array are all of the indices corresponding
        # to that variable's rows or columns in the total jacobian.
        yield idxs, self.par_deriv_matmat_input_setter, self.par_deriv_matmat_jac_setter

    #
    # input setter functions
    #
    def single_input_setter(self, idx):
        """
        Set 1's into the input vector in the single index case.

        Parameters
        ----------
        idx : int
            Total jacobian row or column index.

        Returns
        -------
        set
            Set of relevant system names.
        tuple or None
            vec_name corresponding to the given index (or None).
        int or None
            key used for storage of cached linear solve (if active, else None).
        """
        input_name, vecname, rel_systems, cache_lin_sol = self.input_idx_map[idx]

        loc_idx = self.input_loc_idxs[idx]
        if loc_idx != -1:
            self.input_vec[vecname]._views_flat[input_name][loc_idx] = 1.0

        if cache_lin_sol:
            return rel_systems, (vecname,), idx
        else:
            return rel_systems, None, None

    def simul_coloring_input_setter(self, inds):
        """
        Set 1's into the input vector in the simul coloring case.

        Parameters
        ----------
        inds : list of int
            Total jacobian row or column indices.

        Returns
        -------
        set
            Set of relevant system names.
        tuple of str or None
            'linear' or None if linear solve caching is inactive.
        int or None
            key used for storage of cached linear solve (if active, else None).
        """
        all_rel_systems = set()
        cache = False

        for i in inds:
            rel_systems, vec_names, _ = self.single_input_setter(i)
            _update_rel_systems(all_rel_systems, rel_systems)
            cache |= vec_names is not None

        if cache:
            return all_rel_systems, ('linear',), inds[0]
        else:
            return all_rel_systems, None, None

    def par_deriv_input_setter(self, inds):
        """
        Set 1's into the input vector in the parallel derivative case.

        Parameters
        ----------
        inds : tuple of int
            Total jacobian row or column indices.

        Returns
        -------
        set
            Set of relevant system names.
        list of str or None
            List of vec_names or None if linear solve caching is inactive.
        int or None
            key used for storage of cached linear solve (if active, else None).
        """
        all_rel_systems = set()
        vec_names = []

        for count, i in enumerate(inds):
            rel_systems, vnames, _ = self.single_input_setter(i)
            _update_rel_systems(all_rel_systems, rel_systems)
            if vnames is not None:
                vec_names.append(vnames[0])

        if vec_names:
            return all_rel_systems, vec_names, inds[0]
        else:
            return all_rel_systems, None, None

    def matmat_input_setter(self, inds):
        """
        Set 1's into the input vector in the matrix-matrix case.

        Parameters
        ----------
        inds : ndarray of int
            Total jacobian row or column indices.

        Returns
        -------
        set
            Set of relevant system names.
        tuple of str or None
            (vec_name,) or None if linear solve caching is inactive.
        int or None
            key used for storage of cached linear solve (if active, else None).
        """
        input_vec = self.input_vec
        input_idx_map = self.input_idx_map
        input_loc_idxs = self.input_loc_idxs

        input_name, vec_name, rel_systems, cache_lin_sol = input_idx_map[inds[0]]

        dinputs = input_vec[vec_name]

        for col, i in enumerate(inds):
            loc_idx = input_loc_idxs[i]
            if loc_idx != -1:
                dinputs._views_flat[input_name][loc_idx, col] = 1.0

        if cache_lin_sol:
            return rel_systems, (vec_name,), inds[0]
        else:
            return rel_systems, None, None

    def par_deriv_matmat_input_setter(self, inds):
        """
        Set 1's into the input vector in the matrix matrix with parallel deriv case.

        Parameters
        ----------
        inds : list of ndarray of int
            Total jacobian row or column indices.

        Returns
        -------
        set
            Set of relevant system names.
        list of str or None
            vec_names or None if linear solve caching is inactive.
        int or None
            key used for storage of cached linear solve (if active, else None).
        """
        input_vec = self.input_vec
        input_idx_map = self.input_idx_map
        input_loc_idxs = self.input_loc_idxs

        all_rel_systems = set()
        cache = False

        vec_names = []
        for matmat_idxs in inds:
            input_name, vec_name, rel_systems, cache_lin_sol = input_idx_map[matmat_idxs[0]]
            if cache_lin_sol:
                vec_names.append(vec_name)
            cache |= cache_lin_sol
            _update_rel_systems(all_rel_systems, rel_systems)

            dinputs = input_vec[vec_name]
            ncol = dinputs._ncol

            for col, i in enumerate(matmat_idxs):
                loc_idx = input_loc_idxs[i]
                if loc_idx != -1:
                    if ncol > 1:
                        dinputs._views_flat[input_name][loc_idx, col] = 1.0
                    else:
                        dinputs._views_flat[input_name][loc_idx] = 1.0

        if cache:
            return all_rel_systems, vec_names, inds[0][0]
        else:
            return all_rel_systems, None, None

    #
    # Jacobian setter functions
    #
    def single_jac_setter(self, i):
        """
        Set the appropriate part of the total jacobian for a single input index.

        Parameters
        ----------
        i : int
            Total jacobian row or column index.
        """
        input_name, vecname, _, _ = self.input_idx_map[i]
        out_views = self.output_vec[vecname]._views_flat
        relevant = self.relevant
        fwd = self.fwd
        J = self.J
        nproc = self.comm.size

        for output_name in self.output_list:
            if input_name not in relevant or output_name in relevant[input_name]:
                slc, indices, distrib = self.out_meta[output_name]
                deriv_val = None
                if output_name in out_views:
                    deriv_val = out_views[output_name]
                    if indices is not None:
                        deriv_val = deriv_val[indices]

                if nproc > 1 and not distrib:
                    if deriv_val is None:
                        deriv_val = np.empty(slc.stop - slc.start)
                    self.comm.Bcast(deriv_val, root=self.owning_ranks[output_name])

                # print("deriv_val:", output_name, input_name, deriv_val)
                if fwd:
                    J[slc, i] = deriv_val
                else:
                    J[i, slc] = deriv_val

    def par_deriv_jac_setter(self, inds):
        """
        Set the appropriate part of the total jacobian for multiple input indices.

        Parameters
        ----------
        inds : tuple of int
            Total jacobian row or column indices.
        """
        for i in inds:
            self.single_jac_setter(i)

    def simul_coloring_jac_setter(self, inds):
        """
        Set the appropriate part of the total jacobian for simul coloring input indices.

        Parameters
        ----------
        inds : list of int
            Total jacobian row or column indices.
        """
        row_map = self.simul_coloring[1]
        relevant = self.relevant
        out_meta = self.out_meta
        idx2local = self.idx2local
        idx2name = self._idx2name
        outvecs = self.output_vec
        J = self.J

        for i in inds:
            input_name, vecname, _, _ = self.input_idx_map[i]
            out_views = outvecs[vecname]._views_flat
            for row in row_map[i]:
                output_name = idx2name[row]
                deriv_val = None
                if input_name not in relevant or output_name in relevant[input_name]:
                    if output_name in out_views:
                        deriv_val = out_views[output_name]
                        indices = out_meta[output_name][1]
                        if indices is not None:
                            deriv_val = deriv_val[indices]
                        # print("deriv_val:", i, output_name, input_name, deriv_val)
                        J[row, i] = deriv_val[idx2local[row]]

    def matmat_jac_setter(self, inds):
        """
        Set the appropriate part of the total jacobian for matrix matrix input indices.

        Parameters
        ----------
        inds : ndarray of int
            Total jacobian row or column indices.
        """
        # in plain matmat, all inds are for a single variable for each iteration of the outer loop,
        # so any relevance can be determined only once.
        input_name, vecname, _, _ = self.input_idx_map[inds[0]]
        out_views = self.output_vec[vecname]._views_flat
        ncol = self.output_vec[vecname]._ncol
        relevant = self.relevant
        nproc = self.comm.size
        fwd = self.fwd
        J = self.J
        owning_ranks = self.owning_ranks

        for output_name in self.output_list:
            slc, indices, distrib = self.out_meta[output_name]
            deriv_val = out_idxs = None
            if input_name not in relevant or output_name in relevant[input_name]:
                if output_name in out_views:
                    deriv_val = out_views[output_name]
                    if indices is not None:
                        deriv_val = deriv_val[indices]

                if nproc > 1 and not distrib:
                    if deriv_val is None:
                        deriv_val = np.empty((slc.stop - slc.start, ncol))
                    self.comm.Bcast(deriv_val, root=owning_ranks[output_name])

                if fwd:
                    J[slc, inds] = deriv_val
                else:
                    J[inds, slc] = deriv_val.T

    def par_deriv_matmat_jac_setter(self, inds):
        """
        Set the appropriate part of the total jacobian for par_deriv matrix matrix input indices.

        Parameters
        ----------
        inds : list of ndarray of int
            Total jacobian row or column indices.
        """
        for matmat_idxs in inds:
            self.matmat_jac_setter(matmat_idxs)


def _check_voi_meta(name, parallel_deriv_color, matmat, simul_coloring):
    """
    Check the contents of the given metadata for incompatible options.

    An exception will be raised if options are incompatible.

    Parameters
    ----------
    name : str
        Name of the variable.
    parallel_deriv_color : str
        Color of parallel deriv grouping.
    matmat : bool
        If True, vectorize derivatives for this variable.
    simul_coloring : ndarray
        Array of colors. Each entry corresponds to a column or row of the total jacobian.
    """
    if simul_coloring:
        if parallel_deriv_color:
            raise RuntimeError("Using both simul_coloring and parallel_deriv_color with "
                               "variable '%s' is not supported." % name)
        if matmat:
            raise RuntimeError("Using both simul_coloring and vectorize_derivs with "
                               "variable '%s' is not supported." % name)


def _fix_pdc_lengths(idx_iter_dict):
    """
    Take any parallel_deriv_color entries and make sure their index arrays are same length.

    Parameters
    ----------
    idx_iter_dict : dict
        Dict of a name/color mapped to indexing information.
    """
    for key, tup in iteritems(idx_iter_dict):
        par_deriv_color, matmat, range_list, _ = tup
        if par_deriv_color:
            if not matmat:
                lens = np.array([end - start for start, end in range_list])
                maxlen = np.max(lens)
                diffs = lens - maxlen
            if not matmat and np.any(diffs):
                for i, diff in enumerate(diffs):
                    start, end = range_list[i]
                    if diff < 0:
                        range_list[i] = np.empty(maxlen, dtype=int)
                        range_list[i][:end - start] = np.arange(start, end, dtype=int)
                        range_list[i][end - start:] = range_list[i][end - start - 1]
                    else:
                        range_list[i] = np.arange(start, end, dtype=int)
            else:
                # just convert all (start, end) tuples to aranges
                for i, (start, end) in enumerate(range_list):
                    range_list[i] = np.arange(start, end, dtype=int)


def _update_rel_systems(all_rel_systems, rel_systems):
    """
    Combine all relevant systems in those cases where we have multiple input variables involved.

    Parameters
    ----------
    all_rel_systems : set
        Current set of all relevant system names.
    rel_systems : set
        Set of relevant system names for the latest iteration.
    """
    if all_rel_systems is _contains_all or rel_systems is _contains_all:
        all_rel_systems = _contains_all
    else:
        all_rel_systems.update(rel_systems)
