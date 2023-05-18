Old function to generate custom instances, adapt it here.


def dummy_data(num_scans,
               num_pind = None,
               seed = 0):
               num_pind=None,
               seed=0):
    """Generates realistic(-ish) data for an instance of size num_scans.
    Args:
      num_scans: The total number of scans.
      num_pind: The number of possible indexes to consider (None will use the default values).
      seed: The random seed.
    
    Returns dictionary of:
      num_scans: The number of scans.
      num_eind: The number of existing indexes.
      num_pind: The number of possible indexes.
      cost_eind_0: Cost matrix of E^0.
      cost_eind_r: Cost matrix of E^r.
      cost_eind_b: Cost matrix of E^b.
      cost_pind_0: Cost matrix of C^0.
      cost_pind_r: Cost matrix of C^r.
      cost_pind_b: Cost matrix of C^b.
      cost_read: Cost array of sequential readings.
      eind_iwo: IWO array of the existing indexes.
      pind_iwo: IWO array of the possible indexes.
      spm: Scans per minute metric for each scan.
    """
    random.seed(seed)
    
    # Min/max number of existing and possible indexes.
    min_num_eind = 1
    max_num_eind = 5
    if num_pind is None:
        min_num_pind = 5
        max_num_pind = 20
    else:
        min_num_pind = num_pind
        max_num_pind = num_pind
    # Min/max number of scans covered by an index (as a fraction of the number of scans).
    min_scans_cov = 0.1
    max_scans_cov = 0.25
    
    # Min/max value of the cost of a scan by an index.
    min_index_cost = 1
    max_index_cost = 40
    
    # Min/max value of the cost of a scan by sequential reading.
    min_read_cost = 75
    max_read_cost = 100
    
    # Min/max value for the IWO of an index.
    min_iwo = 0.05
    max_iwo = 0.25
    # Min/max value for the scans per minute.
    min_spm = 0.1
    max_spm = 10
    
    # Generate the data.
    num_eind = random.randint(min_num_eind, max_num_eind)
    num_pind = random.randint(min_num_pind, max_num_pind)
    def generate_cost_base(n):
        """
        Generates a list of lists of tuples for the costs of a set of indexes "base". For example,
        base[2][4] = (7, 21.42) means that for index 2, the 4th scan that it covers is scan 7, and
        the cost associated with that coverage is 21.42.
        """
        base = []
        for index in range(n):
            num_covered_scans = max(round(random.uniform(min_scans_cov, max_scans_cov)*num_scans), 1)
            covered_scans = random.sample(range(num_scans), num_covered_scans)
            covered_scans_costs = [round(random.uniform(min_index_cost, max_index_cost)) for scan in range(num_covered_scans)] # <-- CHANGE TO round(X, 2)
            index = list(zip(covered_scans, covered_scans_costs))
            base.append(index)
        return base
        
    cost_eind_base = generate_cost_base(num_eind)
    cost_pind_base = generate_cost_base(num_pind)
    def generate_cost_0(base):
        """Transforms the cost base into a matrix M^0."""
        matrix = [[0 for _ in range(num_scans)] for _ in range(len(base))]
        for index in range(len(base)):
            for scan in base[index]:
                matrix[index][scan[0]] = scan[1]
        return matrix
    cost_eind_0 = generate_cost_0(cost_eind_base)
    cost_pind_0 = generate_cost_0(cost_pind_base)
    cost_read = [round(random.uniform(min_read_cost, max_read_cost)) for scan in range(num_scans)] # <-- CHANGE TO round(X, 2)
    
    def generate_cost_r(base):
        """Transforms the cost base into a matrix M^r."""
        matrix = [[cost_read[j] for j in range(num_scans)] for _ in range(len(base))]
        for index in range(len(base)):
            for scan in base[index]:
                matrix[index][scan[0]] = scan[1]
        return matrix
    cost_eind_r = generate_cost_r(cost_eind_base)
    cost_pind_r = generate_cost_r(cost_pind_base)
    def generate_cost_b(base):
        """Transforms the cost base into a matrix M^b."""
        matrix = [[0 for _ in range(num_scans)] for _ in range(len(base))]
        for index in range(len(base)):
            for scan in base[index]:
                matrix[index][scan[0]] = 1
        return matrix
    cost_eind_b = generate_cost_b(cost_eind_base)
    cost_pind_b = generate_cost_b(cost_pind_base)
    # eind_iwo = [round(random.uniform(min_iwo, max_iwo), 2) for ei in range(num_eind)]
    # pind_iwo = [round(random.uniform(min_iwo, max_iwo), 2) for pi in range(num_pind)]
    eind_iwo = [round(random.uniform(min_iwo, max_iwo)*100) for ei in range(num_eind)]
    pind_iwo = [round(random.uniform(min_iwo, max_iwo)*100) for pi in range(num_pind)]
    # spm = [round(random.uniform(min_spm, max_spm), 2) for j in range(num_scans)]
    spm = [round(random.uniform(min_spm, max_spm)*10) for j in range(num_scans)]
    
    data = dict()
    data['num_scans'] = num_scans
    data['num_eind'] = num_eind
    data['num_pind'] = num_pind
    data['cost_eind_0'] = cost_eind_0
    data['cost_eind_r'] = cost_eind_r
    data['cost_eind_b'] = cost_eind_b
    data['cost_pind_0'] = cost_pind_0
    data['cost_pind_r'] = cost_pind_r
    data['cost_pind_b'] = cost_pind_b
    data['cost_read'] = cost_read
    data['eind_iwo'] = eind_iwo
    data['pind_iwo'] = pind_iwo
    data['spm'] = spm
    return data
