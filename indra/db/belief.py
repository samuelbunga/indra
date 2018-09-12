
class LoadError(Exception):
    pass


class MockStatement(object):
    """A class to imitate real INDRA Statements for calculating belief."""
    def __init__(self, mk_hash, evidence=None, supports=None, supported_by=None):
        if isinstance(evidence, list):
            self.evidence = evidence
        elif evidence is None:
            self.evidence = []
        else:
            self.evidence = [evidence]
        self.__mk_hash = mk_hash
        if supports:
            self.supports = supports
        else:
            self.supports = []
        if supported_by:
            self.supported_by = supported_by
        else:
            self.supported_by = []
        self.belief = None

    def matches_key(self):
        return self.__mk_hash


class MockEvidence(object):
    """A class to imitate real INDRA Evidence for calculating belief."""
    def __init__(self, source_api, **annotations):
        self.source_api = source_api

        # Some annotations are used in indra.belief.tag_evidence_subtype.
        # TODO: optionally implement necessary annotations.
        self.annotations = annotations.copy()


def populate_support(stmts, links):
    """Populate the supports supported_by lists of statements given links.

    Parameters
    ----------
    stmts : list[MockStatement/Statement]
        A list of objects with supports and supported_by attributes which are
        lists or equivalent.
    links : list[tuple]
        A list of pairs of hashes or matches_keys, where the first supports the
        second.
    """
    stmt_dict = {s.matches_key(): s for s in stmts}
    for supped_idx, supping_idx in links:
        stmt_dict[supping_idx].supports.append(stmt_dict[supped_idx])
        stmt_dict[supped_idx].supported_by.append(stmt_dict[supping_idx])
    return


def load_mock_statements(db):
    """Generate a list of mock statements from the pa statement table."""
    res_rdg = db.select_all([db.Reading.reader,
                             db.RawUniqueLinks.pa_stmt_mk_hash,
                             db.RawUniqueLinks.raw_stmt_id],
                            *db.link(db.Reading, db.RawUniqueLinks))
    res_dbs = db.select_all([db.DBInfo.db_name,
                             db.RawUniqueLinks.pa_stmt_mk_hash,
                             db.RawUniqueLinks.raw_stmt_id],
                            *db.link(db.DBInfo, db.RawUniqueLinks))
    stmts_dict = {}
    for src_api, mk_hash, sid in res_rdg + res_dbs:
        # If the statement is new, add it to the dict.
        if mk_hash not in stmts_dict.keys():
            stmts_dict[mk_hash] = MockStatement(mk_hash)

        # Add the new evidence.
        stmts_dict[mk_hash].evidence.append(MockEvidence(src_api, raw_sid=sid))

    return list(stmts_dict.values())
