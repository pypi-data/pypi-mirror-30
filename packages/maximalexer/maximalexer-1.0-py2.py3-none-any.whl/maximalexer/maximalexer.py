from pygments.lexer import RegexLexer, words, include, bygroups, using, \
    this, default
from pygments.token import Text, Comment, Operator, Keyword, Name, \
    Number, Punctuation, String

__all__ = ['MaximaLexer']


class MaximaLexer(RegexLexer):
    """
    For `Maxima`_ source code.

    .. versionadded:: 1.2
    """
    name = 'Maxima'
    aliases = ['maxima']
    filenames = ['*.mac']
    mimetypes = ['text/x-maxima']

    #: optional Comment or Whitespace
    _ws = r'(?:\s|//.*?\n|/\*.*?\*/)+'

    tokens = {
        'whitespace': [
            (r'\n', Text),
            (r'\s+', Text),
            (r'\\\n', Text),  # line continuation
            (r'//(\n|(.|\n)*?[^\\]\n)', Comment),
            (r'/(\\\n)?\*(.|\n)*?\*(\\\n)?/', Comment),
        ],
        'statements': [
            # simple string (TeX friendly)
            (r'"(\\\\|\\"|[^"])*"', String),
            # C style string (with character escapes)
            (r"'", String, 'string'),
            (r'(\d+\.\d*|\.\d+|\d+)[eE][+-]?\d+[lL]?', Number.Float),
            (r'(\d+\.\d*|\.\d+|\d+[fF])[fF]?', Number.Float),
            (r'0x[0-9a-fA-F]+[Ll]?', Number.Hex),
            (r'0[0-7]+[Ll]?', Number.Oct),
            (r'\d+[Ll]?', Number.Integer),
            (r'[~!%^&*+=|?:<>/-]', Operator),
            (r'[()\[\]\{\},.;$]', Punctuation),
            (r'\b(case)(.+?)(:)', bygroups(Keyword, using(this), Text)),
            (r'(and|do|else|elseif|false|for|if|in|not|or|step|then|thru|'
             r'true|while)\b', Keyword),
            # Since an asy-type-name can be also an asy-function-name,
            # in the following we test if the string "  [a-zA-Z]" follows
            # the Keyword.Type.
            # Of course it is not perfect !
            (r'(abasep|abs|absint|absolute_real_time|acos|acosh|acot|acoth|'
            r'acsc|acsch|activate|addcol|add_edge|add_edges|addmatrices|addrow|'
            r'add_vertex|add_vertices|adjacency_matrix|adjoin|adjoint|af|agd|airy_ai|'
            r'airy_bi|airy_dai|airy_dbi|algsys|alg_type|alias|allroots|alphacharp|'
            r'alphanumericp|antid|antidiff|AntiDifference|append|appendfile|apply|apply1|'
            r'apply2|applyb1|apropos|args|arithmetic|arithsum|array|arrayapply|'
            r'arrayinfo|arraymake|ascii|asec|asech|asin|asinh|askinteger|'
            r'asksign|assoc|assoc_legendre_p|assoc_legendre_q|assume|asympa|at|atan|'
            r'atan2|atanh|atensimp|atom|atvalue|augcoefmatrix|augmented_lagrangian_method|av|'
            r'average_degree|backtrace|barsplot|bashindices|batch|batchload|bc2|bdvac|'
            r'belln|bern|bernpoly|bessel|bessel_i|bessel_j|bessel_k|bessel_y|'
            r'beta|bezout|bffac|bfhzeta|bfloat|bfloatp|bfpsi|bfpsi0|'
            r'bfzeta|biconected_components|bimetric|binomial|bipartition|block|blockmatrixp|bode_gain|'
            r'bode_phase|bothcoef|box|boxplot|break|bug_report|build_info|buildq|'
            r'burn|cabs|canform|canten|cardinality|carg|cartan|cartesian_product|'
            r'catch|cbffac|cdf_bernoulli|cdf_beta|cdf_binomial|cdf_cauchy|cdf_chi2|cdf_continuous_uniform|'
            r'cdf_discrete_uniform|cdf_exp|cdf_f|cdf_gamma|cdf_geometric|cdf_gumbel|cdf_hypergeometric|cdf_laplace|'
            r'cdf_logistic|cdf_lognormal|cdf_negative_binomial|cdf_normal|cdf_pareto|cdf_poisson|cdf_rank_sum|cdf_rayleigh|'
            r'cdf_signed_rank|cdf_student_t|cdf_weibull|cdisplay|ceiling|central_moment|cequal|cequalignore|'
            r'cf|cfdisrep|cfexpand|cgeodesic|cgreaterp|cgreaterpignore|changename|changevar|'
            r'chaosgame|charat|charfun|charfun2|charlist|charp|charpoly|chebyshev_t|'
            r'chebyshev_u|checkdiv|check_overlaps|cholesky|christof|chromatic_index|chromatic_number|cint|'
            r'circulant_graph|clear_edge_weight|clear_rules|clear_vertex_label|clebsch_graph|clessp|clesspignore|close|'
            r'closefile|cmetric|coeff|coefmatrix|cograd|col|collapse|collectterms|'
            r'columnop|columnspace|columnswap|columnvector|combination|combine|comp2pui|compare|'
            r'compfile|compile|compile_file|complement_graph|complete_bipartite_graph|complete_graph|components|concan|'
            r'concat|conjugate|conmetderiv|connected_components|connect_vertices|cons|constantp|constituent|'
            r'cont2part|content|continuous_freq|contortion|contour_plot|contract|contract_edge|contragrad|'
            r'contrib_ode|convert|coord|copy|copy_graph|copylist|copymatrix|cor|'
            r'cos|cosh|cot|coth|cov|cov1|covdiff|covect|'
            r'covers|create_graph|create_list|csc|csch|csetup|cspline|ctaylor|'
            r'ct_coordsys|ctransform|ctranspose|cube_graph|cunlisp|cv|cycle_digraph|cycle_graph|'
            r'dblint|deactivate|declare|declare_translated|declare_weight|decsym|defcon|define|'
            r'define_variable|defint|defmatch|defrule|deftaylor|degree_sequence|del|delete|'
            r'deleten|delta|demo|demoivre|denom|depends|derivdegree|derivlist|'
            r'describe|desolve|determinant|dgauss_a|dgauss_b|dgeev|dgesvd|diag|'
            r'diagmatrix|diag_matrix|diagmatrixp|diameter|diff|digitcharp|dimacs_export|dimacs_import|'
            r'dimension|direct|discrete_freq|disjoin|disjointp|disolate|disp|dispcon|'
            r'dispform|dispfun|dispJordan|display|disprule|dispterms|distrib|divide|'
            r'divisors|divsum|dkummer_m|dkummer_u|dlange|dodecahedron_graph|dotproduct|dotsimp|'
            r'dpart|draw|draw2d|draw3d|draw_graph|dscalar|echelon|edge_coloring|'
            r'edges|eigens_by_jacobi|eigenvalues|eigenvectors|eighth|einstein|eivals|eivects|'
            r'elapsed_real_time|elapsed_run_time|ele2comp|ele2polynome|ele2pui|elem|elementp|eliminate|'
            r'elliptic_e|elliptic_ec|elliptic_eu|elliptic_f|elliptic_kc|elliptic_pi|ematrix|empty_graph|'
            r'emptyp|endcons|entermatrix|entertensor|entier|equal|equalp|equiv_classes|'
            r'erf|errcatch|error|errormsg|euler|ev|eval_string|evenp|'
            r'every|evolution|evolution2d|evundiff|example|exp|expand|expandwrt|'
            r'expandwrt_factored|explose|exponentialize|express|expt|exsec|extdiff|extract_linear_equations|'
            r'extremal_subset|ezgcd|f90|facsum|factcomb|factor|factorfacsum|factorial|'
            r'factorout|factorsum|facts|fast_central_elements|fast_linsolve|fasttimes|featurep|fft|'
            r'fib|fibtophi|fifth|filename_merge|file_search|file_type|fillarray|findde|'
            r'find_root|first|fix|flatten|flength|float|floatnump|floor|'
            r'flower_snark|flush|flush1deriv|flushd|flushnd|forget|fortran|fourcos|'
            r'fourexpand|fourier|fourint|fourintcos|fourintsin|foursimp|foursin|fourth|'
            r'fposition|frame_bracket|freeof|freshline|from_adjacency_matrix|frucht_graph|full_listify|fullmap|'
            r'fullmapl|fullratsimp|fullratsubst|fullsetify|funcsolve|fundef|funmake|funp|'
            r'gamma|gauss_a|gauss_b|gaussprob|gcd|gcdex|gcdivide|gcfac|'
            r'gcfactor|gd|genfact|gen_laguerre|genmatrix|geometric|geometric_mean|geosum|'
            r'get|get_edge_weight|get_lu_factors|get_pixel|get_vertex_label|gfactor|gfactorsum|ggf|'
            r'girth|global_variances|gnuplot_close|gnuplot_replot|gnuplot_reset|gnuplot_restart|gnuplot_start|go|'
            r'Gosper|GosperSum|gradef|gramschmidt|graph6_decode|graph6_encode|graph6_export|graph6_import|'
            r'graph_center|graph_charpoly|graph_eigenvalues|graph_order|graph_periphery|graph_product|graph_size|graph_union|'
            r'grid_graph|grind|grobner_basis|grotzch_graph|hamilton_cycle|hamilton_path|hankel|harmonic|'
            r'harmonic_mean|hav|heawood_graph|hermite|hessian|hilbert_matrix|hipow|histogram|'
            r'hodge|horner|ic1|ic2|ic_convert|ichr1|ichr2|icosahedron_graph|'
            r'icurvature|ident|identfor|identity|idiff|idim|idummy|ieqn|'
            r'ifactors|iframes|ifs|ift|igeodesic_coords|ilt|imagpart|imetric|'
            r'implicit_derivative|implicit_plot|indexed_tensor|indices|induced_subgraph|inferencep|inference_result|infix|'
            r'init_atensor|init_ctensor|in_neighbors|innerproduct|inpart|inprod|inrt|integerp|'
            r'integer_partitions|integrate|intersect|intersection|intervalp|intopois|intosum|invariant1|'
            r'invariant2|inverse_jacobi_cd|inverse_jacobi_cn|inverse_jacobi_cs|inverse_jacobi_dc|inverse_jacobi_dn|inverse_jacobi_ds|inverse_jacobi_nc|'
            r'inverse_jacobi_nd|inverse_jacobi_ns|inverse_jacobi_sc|inverse_jacobi_sd|inverse_jacobi_sn|invert|invert_by_lu|inv_mod|'
            r'is|is_biconnected|is_bipartite|is_connected|is_digraph|is_edge_in_graph|is_graph|is_graph_or_digraph|'
            r'ishow|is_isomorphic|isolate|isomorphism|is_planar|isqrt|is_sconnected|is_tree|'
            r'is_vertex_in_graph|items_inference|jacobi|jacobian|jacobi_cd|jacobi_cn|jacobi_cs|jacobi_dc|'
            r'jacobi_dn|jacobi_ds|jacobi_nc|jacobi_nd|jacobi_ns|jacobi_p|jacobi_sc|jacobi_sd|'
            r'jacobi_sn|JF|join|jordan|julia|kdels|kdelta|kill|'
            r'killcontext|kostka|kron_delta|kronecker_product|kummer_m|kummer_u|kurtosis|kurtosis_bernoulli|'
            r'kurtosis_beta|kurtosis_binomial|kurtosis_chi2|kurtosis_continuous_uniform|kurtosis_discrete_uniform|kurtosis_exp|kurtosis_f|kurtosis_gamma|'
            r'kurtosis_geometric|kurtosis_gumbel|kurtosis_hypergeometric|kurtosis_laplace|kurtosis_logistic|kurtosis_lognormal|kurtosis_negative_binomial|kurtosis_normal|'
            r'kurtosis_pareto|kurtosis_poisson|kurtosis_rayleigh|kurtosis_student_t|kurtosis_weibull|labels|lagrange|laguerre|'
            r'lambda|laplace|laplacian_matrix|last|lbfgs|lc2kdt|lcharp|lc_l|'
            r'lcm|lc_u|ldefint|ldisp|ldisplay|legendre_p|legendre_q|leinstein|'
            r'length|let|letrules|letsimp|levi_civita|lfreeof|lgtreillis|lhs|'
            r'li|liediff|limit|Lindstedt|linear|linearinterpol|linear_program|line_graph|'
            r'linsolve|listarray|list_correlations|listify|list_nc_monomials|listoftens|listofvars|listp|'
            r'lmax|lmin|load|loadfile|local|locate_matrix_entry|log|logand|'
            r'logarc|logcontract|logor|logxor|lopow|lorentz_gauge|lowercasep|lpart|'
            r'lratsubst|lreduce|lriemann|lsquares_estimates|lsquares_estimates_approximate|lsquares_estimates_exact|lsquares_mse|lsquares_residual_mse|'
            r'lsquares_residuals|lsum|ltreillis|lu_backsub|lu_factor|macroexpand|macroexpand1|make_array|'
            r'makebox|makefact|makegamma|make_level_picture|makelist|makeOrders|make_poly_continent|make_poly_country|'
            r'make_polygon|make_random_state|make_rgb_picture|makeset|make_transform|mandelbrot|map|mapatom|'
            r'maplist|matchdeclare|matchfix|mat_cond|mat_fullunblocker|mat_function|mat_norm|matrix|'
            r'matrixmap|matrixp|matrix_size|mattrace|mat_trace|mat_unblocker|max|max_clique|'
            r'max_degree|max_flow|maxi|maximize_lp|max_independent_set|max_matching|maybe|mean|'
            r'mean_bernoulli|mean_beta|mean_binomial|mean_chi2|mean_continuous_uniform|mean_deviation|mean_discrete_uniform|mean_exp|'
            r'mean_f|mean_gamma|mean_geometric|mean_gumbel|mean_hypergeometric|mean_laplace|mean_logistic|mean_lognormal|'
            r'mean_negative_binomial|mean_normal|mean_pareto|mean_poisson|mean_rayleigh|mean_student_t|mean_weibull|median|'
            r'median_deviation|member|metricexpandall|min|min_degree|minfactorial|mini|minimalPoly|'
            r'minimize_lp|minimum_spanning_tree|minor|mnewton|mod|mode_declare|mode_identity|ModeMatrix|'
            r'moebius|mon2schur|mono|monomial_dimensions|multi_elem|multinomial|multinomial_coeff|multi_orbit|'
            r'multi_pui|multsym|multthru|mycielski_graph|nary|nc_degree|ncexpt|ncharpoly|'
            r'negative_picture|neighbors|newcontext|newdet|new_graph|newline|newton|next_prime|'
            r'niceindices|ninth|noncentral_moment|nonmetricity|nonnegintegerp|nonscalarp|nonzeroandfreeof|notequal|'
            r'nounify|nptetrad|nroots|nterms|ntermst|nthroot|nullity|nullspace|'
            r'num|numbered_boundaries|numberp|num_distinct_partitions|numerval|numfactor|num_partitions|nusum|'
            r'odd_girth|oddp|ode2|ode_check|odelin|op|opena|openr|'
            r'openw|operatorp|opsubst|optimize|orbit|orbits|ordergreat|ordergreatp|'
            r'orderless|orderlessp|orthogonal_complement|orthopoly_recur|orthopoly_weight|outermap|out_neighbors|outofpois|'
            r'pade|parGosper|parse_string|part|part2cont|partfrac|partition|partition_set|'
            r'partpol|path_digraph|path_graph|pdf_bernoulli|pdf_beta|pdf_binomial|pdf_cauchy|pdf_chi2|'
            r'pdf_continuous_uniform|pdf_discrete_uniform|pdf_exp|pdf_f|pdf_gamma|pdf_geometric|pdf_gumbel|pdf_hypergeometric|'
            r'pdf_laplace|pdf_logistic|pdf_lognormal|pdf_negative_binomial|pdf_normal|pdf_pareto|pdf_poisson|pdf_rank_sum|'
            r'pdf_rayleigh|pdf_signed_rank|pdf_student_t|pdf_weibull|pearson_skewness|permanent|permut|permutation|'
            r'permutations|petersen_graph|petrov|pickapart|picture_equalp|picturep|piechart|planar_embedding|'
            r'playback|plog|plot2d|plot3d|plotdf|plsquares|pochhammer|poisdiff|'
            r'poisexpt|poisint|poismap|poisplus|poissimp|poissubst|poistimes|poistrim|'
            r'polarform|polartorect|poly_add|poly_buchberger|poly_buchberger_criterion|poly_colon_ideal|poly_content|polydecomp|'
            r'poly_depends_p|poly_elimination_ideal|poly_exact_divide|poly_expand|poly_expt|poly_gcd|poly_grobner|poly_grobner_equal|'
            r'poly_grobner_member|poly_grobner_subsetp|poly_ideal_intersection|poly_ideal_polysaturation|poly_ideal_polysaturation1|poly_ideal_saturation|poly_ideal_saturation1|poly_lcm|'
            r'poly_minimization|polymod|poly_multiply|polynome2ele|polynomialp|poly_normal_form|poly_normalize|poly_normalize_list|'
            r'poly_polysaturation_extension|poly_primitive_part|poly_pseudo_divide|poly_reduced_grobner|poly_reduction|poly_saturation_extension|poly_s_polynomial|poly_subtract|'
            r'polytocompanion|potential|power_mod|powers|powerseries|powerset|prev_prime|primep|'
            r'print|printf|print_graph|printpois|printprops|prodrac|product|properties|'
            r'propvars|psi|ptriangularize|pui|pui2comp|pui2ele|pui2polynome|pui_direct|'
            r'puireduc|put|qput|qrange|quad_qag|quad_qagi|quad_qags|quad_qawc|'
            r'quad_qawf|quad_qawo|quad_qaws|quantile|quantile_bernoulli|quantile_beta|quantile_binomial|quantile_cauchy|'
            r'quantile_chi2|quantile_continuous_uniform|quantile_discrete_uniform|quantile_exp|quantile_f|quantile_gamma|quantile_geometric|quantile_gumbel|'
            r'quantile_hypergeometric|quantile_laplace|quantile_logistic|quantile_lognormal|quantile_negative_binomial|quantile_normal|quantile_pareto|quantile_poisson|'
            r'quantile_rayleigh|quantile_student_t|quantile_weibull|quartile_skewness|quit|qunit|quotient|radcan|'
            r'radius|random|random_bernoulli|random_beta|random_binomial|random_cauchy|random_chi2|random_continuous_uniform|'
            r'random_digraph|random_discrete_uniform|random_exp|random_f|random_gamma|random_geometric|random_graph|random_graph1|'
            r'random_gumbel|random_hypergeometric|random_laplace|random_logistic|random_lognormal|random_negative_binomial|random_network|random_normal|'
            r'random_pareto|random_permutation|random_poisson|random_rayleigh|random_regular_graph|random_student_t|random_tournament|random_tree|'
            r'random_weibull|range|rank|rat|ratcoef|ratdenom|ratdiff|ratdisrep|'
            r'ratexpand|rational|rationalize|ratnumer|ratnump|ratp|ratsimp|ratsubst|'
            r'ratvars|ratweight|read|read_hashed_array|readline|read_lisp_array|read_list|read_matrix|'
            r'read_maxima_array|read_nested_list|readonly|read_xpm|realpart|realroots|rearray|rectform|'
            r'recttopolar|rediff|reduce_consts|reduce_order|region_boundaries|rem|remainder|remarray|'
            r'rembox|remcomps|remcon|remcoord|remfun|remfunction|remlet|remove|'
            r'remove_edge|remove_vertex|rempart|remrule|remsym|remvalue|rename|reset|'
            r'residue|resolvante|resolvante_alternee1|resolvante_bipartite|resolvante_diedrale|resolvante_klein|resolvante_klein3|resolvante_produit_sym|'
            r'resolvante_unitaire|resolvante_vierer|rest|resultant|return|reveal|reverse|revert|'
            r'revert2|rgb2level|rhs|ricci|riemann|rinvariant|risch|rk|'
            r'rncombine|romberg|room|rootscontract|row|rowop|rowswap|rreduce|'
            r'run_testsuite|save|scalarp|scaled_bessel_i|scaled_bessel_i0|scaled_bessel_i1|scalefactors|scanmap|'
            r'scatterplot|schur2comp|sconcat|scopy|scsimp|scurvature|sdowncase|sec|'
            r'sech|second|sequal|sequalignore|setdifference|set_edge_weight|setelmx|setequalp|'
            r'setify|setp|set_partitions|set_plot_option|set_random_state|setunits|setup_autoload|set_up_dot_simplifications|'
            r'set_vertex_label|seventh|sexplode|sf|shortest_path|show|showcomps|showratvars|'
            r'sign|signum|similaritytransform|simple_linear_regression|simplify_sum|simplode|simpmetderiv|simtran|'
            r'sin|sinh|sinsert|sinvertcase|sixth|skewness|skewness_bernoulli|skewness_beta|'
            r'skewness_binomial|skewness_chi2|skewness_continuous_uniform|skewness_discrete_uniform|skewness_exp|skewness_f|skewness_gamma|skewness_geometric|'
            r'skewness_gumbel|skewness_hypergeometric|skewness_laplace|skewness_logistic|skewness_lognormal|skewness_negative_binomial|skewness_normal|skewness_pareto|'
            r'skewness_poisson|skewness_rayleigh|skewness_student_t|skewness_weibull|slength|smake|smismatch|solve|'
            r'solve_rec|solve_rec_rat|some|somrac|sort|sparse6_decode|sparse6_encode|sparse6_export|'
            r'sparse6_import|specint|spherical_bessel_j|spherical_bessel_y|spherical_hankel1|spherical_hankel2|spherical_harmonic|splice|'
            r'split|sposition|sprint|sqfr|sqrt|sqrtdenest|sremove|sremovefirst|'
            r'sreverse|ssearch|ssort|sstatus|ssubst|ssubstfirst|staircase|status|'
            r'std|std1|std_bernoulli|std_beta|std_binomial|std_chi2|std_continuous_uniform|std_discrete_uniform|'
            r'std_exp|std_f|std_gamma|std_geometric|std_gumbel|std_hypergeometric|std_laplace|std_logistic|'
            r'std_lognormal|std_negative_binomial|std_normal|std_pareto|std_poisson|std_rayleigh|std_student_t|std_weibull|'
            r'stirling|stirling1|stirling2|strim|striml|strimr|string|stringout|'
            r'stringp|strong_components|sublis|sublist|sublist_indices|submatrix|subsample|subset|'
            r'subsetp|subst|substinpart|substpart|substring|subvar|subvarp|sum|'
            r'sumcontract|summand_to_rec|supcase|supcontext|symbolp|symmdifference|symmetricp|system|'
            r'take_channel|take_inference|tan|tanh|taylor|taylorinfo|taylorp|taylor_simplifier|'
            r'taytorat|tcl_output|tcontract|tellrat|tellsimp|tellsimpafter|tentex|tenth|'
            r'test_mean|test_means_difference|test_normality|test_rank_sum|test_sign|test_signed_rank|test_variance|test_variance_ratio|'
            r'tex|texput|%th|third|throw|time|timedate|timer|'
            r'timer_info|tldefint|tlimit|todd_coxeter|toeplitz|tokens|to_lisp|topological_sort|'
            r'totaldisrep|totalfourier|totient|tpartpol|trace|tracematrix|trace_options|translate|'
            r'translate_file|transpose|tree_reduce|treillis|treinat|triangularize|trigexpand|trigrat|'
            r'trigreduce|trigsimp|trunc|tr_warnings_get|ueivects|uforget|ultraspherical|underlying_graph|'
            r'undiff|union|unique|uniteigenvectors|unit_step|unitvector|unknown|unorder|'
            r'unsum|untellrat|untimer|untrace|uppercasep|uricci|uriemann|uvect|'
            r'vandermonde_matrix|var|var1|var_bernoulli|var_beta|var_binomial|var_chi2|var_continuous_uniform|'
            r'var_discrete_uniform|var_exp|var_f|var_gamma|var_geometric|var_gumbel|var_hypergeometric|var_laplace|'
            r'var_logistic|var_lognormal|var_negative_binomial|var_normal|var_pareto|var_poisson|var_rayleigh|var_student_t|'
            r'var_weibull|vectorpotential|vectorsimp|verbify|vers|vertex_coloring|vertex_degree|vertex_distance|'
            r'vertex_eccentricity|vertex_in_degree|vertex_out_degree|vertices|vertices_to_cycle|vertices_to_path|weyl|wheel_graph|'
            r'with_stdout|write_data|writefile|wronskian|xgraph_curves|xreduce|xthru|Zeilberger|'
            r'zeroequiv|zerofor|zeromatrix|zeromatrixp|zeta|zlange)\b', Keyword.Type),
            # Now the asy-type-name which are not asy-function-name
            # except yours !
            # Perhaps useless
            (r'(_|__|%|%%|absboxchar|activecontexts|additive|algebraic|algepsilon|'
            r'algexact|aliases|all_dotsimp_denoms|allbut|allsym|arrays|askexp|assume_pos|assume_pos_pred|'
            r'assumescalar|atomgrad|backsubst|berlefact|besselexpand|bftorat|bftrunc|boxchar|breakup|'
            r'cauchysum|cflength|cframe_flag|cnonmet_flag|context|contexts|cosnpiflag|ctaypov|ctaypt|'
            r'ctayswitch|ctayvar|ct_coords|ctorsion_flag|ctrgsimp|current_let_rule_package|debugmode|default_let_rule_package|demoivre|'
            r'dependencies|derivabbrev|derivsubst|detout|diagmetric|dim|dispflag|display2d|display_format_internal|'
            r'doallmxops|domain|domxexpt|domxmxops|domxnctimes|dontfactor|doscmxops|doscmxplus|dot0nscsimp|'
            r'dot0simp|dot1simp|dotassoc|dotconstrules|dotdistrib|dotexptsimp|dotident|dotscrules|draw_graph_program|'
            r'%edispflag|%emode|%enumer|epsilon_lp|erfflag|error|error_size|error_syms|%e_to_numlog|'
            r'evflag|evfun|expandwrt_denom|expon|exponentialize|expop|exptdispflag|exptisolate|exptsubst|'
            r'facexpand|factlim|factorflag|file_output_append|file_search_demo|file_search_lisp|file_search_maxima|find_root_abs|find_root_error|'
            r'find_root_rel|flipflag|float2bf|fortindent|fortspaces|fpprec|fpprintprec|functions|gammalim|'
            r'gdet|genindex|gensumnum|GGFCFMAX|GGFINFINITY|globalsolve|gradefs|grind|halfangles|'
            r'%iargs|ibase|icounter|idummyx|ieqnprint|iframe_bracket_form|igeowedge_flag|imetric|inchar|'
            r'infeval|inflag|infolists|in_netmath|integrate_use_rootsof|integration_constant|integration_constant_counter|intfaclim|isolate_wrt_times|'
            r'keepfloat|labels|letrat|let_rule_packages|lhospitallim|limsubst|linechar|linel|linenum|'
            r'linsolve_params|linsolvewarn|lispdisp|listarith|listconstvars|listdummyvars|lmxchar|loadprint|logabs|'
            r'logarc|logconcoeffp|logexpand|lognegint|lognumer|logsimp|m1pbranch|macroexpansion|maperror|'
            r'mapprint|matrix_element_add|matrix_element_mult|matrix_element_transpose|maxapplydepth|maxapplyheight|maxima_tempdir|maxima_userdir|maxnegex|'
            r'maxposex|maxpsifracdenom|maxpsifracnum|maxpsinegint|maxpsiposint|maxtayorder|method|mode_check_errorp|mode_checkp|'
            r'mode_check_warnp|modulus|multiplicities|myoptions|negdistrib|negsumdispflag|newtonepsilon|newtonmaxiter|niceindicespref|'
            r'nolabels|nonegative_lp|noundisp|obase|opproperties|opsubst|optimprefix|optionset|outchar|'
            r'packagefile|partswitch|pfeformat|%piargs|piece|plot_options|poislim|poly_coefficient_ring|poly_elimination_order|'
            r'poly_grobner_algorithm|poly_grobner_debug|poly_monomial_order|poly_primary_elimination_order|poly_return_term_list|poly_secondary_elimination_order|poly_top_reduction_only|powerdisp|prederror|'
            r'primep_number_of_tests|product_use_gamma|programmode|prompt|psexpand|radexpand|radsubstflag|random_beta_algorithm|random_binomial_algorithm|'
            r'random_chi2_algorithm|random_exp_algorithm|random_f_algorithm|random_gamma_algorithm|random_geometric_algorithm|random_hypergeometric_algorithm|random_negative_binomial_algorithm|random_normal_algorithm|random_poisson_algorithm|'
            r'random_student_t_algorithm|ratalgdenom|ratchristof|ratdenomdivide|rateinstein|ratepsilon|ratexpand|ratfac|ratmx|'
            r'ratprint|ratriemann|ratsimpexpons|ratvars|ratweights|ratweyl|ratwtlvl|realonly|refcheck|'
            r'rmxchar|%rnum_list|rombergabs|rombergit|rombergmin|rombergtol|rootsconmode|rootsepsilon|savedef|'
            r'savefactors|scalarmatrixp|setcheck|setcheckbreak|setval|showtime|simplify_products|simpsum|sinnpiflag|'
            r'solvedecomposes|solveexplicit|solvefactors|solve_inconsistent_error|solvenullwarn|solveradcan|solvetrigwarn|sparse|sqrtdispflag|'
            r'stardisp|stats_numer|stringdisp|sublis_apply_lambda|sumexpand|sumsplitfact|taylordepth|taylor_logexpand|taylor_order_coefficients|'
            r'taylor_truncate_polynomials|tensorkill|testsuite_files|timer_devalue|tlimswitch|transcompile|transrun|tr_array_as_ref|tr_bound_function_applyp|'
            r'tr_file_tty_messagesp|tr_float_can_branch_complex|tr_function_call_default|trigexpandplus|trigexpandtimes|triginverses|trigsign|tr_numer|tr_optimize_max_loop|'
            r'tr_semicompile|tr_state_vars|tr_warn_bad_function_calls|tr_warn_fexpr|tr_warn_meval|tr_warn_mode|tr_warn_undeclared|tr_warn_undefined_variable|tr_windy|'
            r'ttyoff|use_fast_arrays|values|vect_cross|verbose|zerobern|zeta%pi|'
            r'tickvalues|tree|triple|vertex|void)\b', Keyword.Type),
            ('[a-zA-Z_]\w*:(?!:)', Name.Label),
            ('[a-zA-Z_]\w*', Name),
        ],
        'root': [
            include('whitespace'),
            # functions
            (r'((?:[\w*\s])+?(?:\s|\*))'  # return arguments
             r'([a-zA-Z_]\w*)'            # method name
             r'(\s*\([^;]*?\))'           # signature
             r'(' + _ws + r')(\{)',
             bygroups(using(this), Name.Function, using(this), using(this),
                      Punctuation),
             'function'),
            # function declarations
            (r'((?:[\w*\s])+?(?:\s|\*))'  # return arguments
             r'([a-zA-Z_]\w*)'            # method name
             r'(\s*\([^;]*?\))'           # signature
             r'(' + _ws + r')(;)',
             bygroups(using(this), Name.Function, using(this), using(this),
                      Punctuation)),
            default('statement'),
        ],
        'statement': [
            include('whitespace'),
            include('statements'),
            ('[{}]', Punctuation),
            (';', Punctuation, '#pop'),
        ],
        'function': [
            include('whitespace'),
            include('statements'),
            (';', Punctuation),
            (r'\{', Punctuation, '#push'),
            (r'\}', Punctuation, '#pop'),
        ],
        'string': [
            (r"'", String, '#pop'),
            (r'\\([\\abfnrtv"\'?]|x[a-fA-F0-9]{2,4}|[0-7]{1,3})', String.Escape),
            (r'\n', String),
            (r"[^\\'\n]+", String),  # all other characters
            (r'\\\n', String),
            (r'\\n', String),        # line continuation
            (r'\\', String),         # stray backslash
        ],
    }

    def get_tokens_unprocessed(self, text):
        from pygments.lexers._asy_builtins import ASYFUNCNAME, ASYVARNAME
        for index, token, value in \
                RegexLexer.get_tokens_unprocessed(self, text):
            if token is Name and value in ASYFUNCNAME:
                token = Name.Function
            elif token is Name and value in ASYVARNAME:
                token = Name.Variable
            yield index, token, value
