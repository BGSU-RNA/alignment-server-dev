from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker

from r3d2msa.db.hub import models
import rnastructure.util.unit_ids as uid


class ProcessingException(Exception):
    """Raised when we can't process a range in the database.
    """
    pass


class Session(object):
    def __init__(self, builder):
        self.builder = builder

    @contextmanager
    def __call__(self):
        session = self.builder()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
        finally:
            session.close()


class Hub(object):
    def __init__(self, engine):
        self.session = Session(sessionmaker(bind=engine))
        models.reflect(engine)

    def units(self, start, stop):
        """Get all units between start and stop. This assumes that both start
        and stop exist and are the results of parsing the new style unit ids.
        In addition, we do allow the model to be missing and let it default to
        1. The base of the unit is ignored.

        :returns: A list of new style ids, in no particular order.
        """

        PdbUnitOrdering = models.PdbUnitOrdering
        PdbUnitIdCorrespondence = models.PdbUnitIdCorrespondence
        PdbCoordinates = models.PdbCoordinates

        start_index = self.index_of(start)
        stop_index = self.index_of(stop)

        if start_index is None:
            generator = uid.UnitIdGenerator()
            raise ProcessingException("Could not find %s" % generator(start))

        if stop_index is None:
            generator = uid.UnitIdGenerator()
            raise ProcessingException("Could not find %s" % generator(stop))

        with self.session() as session:
            query = session.query(PdbUnitIdCorrespondence.unit_id).\
                join(PdbCoordinates,
                     PdbCoordinates.id == PdbUnitIdCorrespondence.old_id).\
                join(PdbUnitOrdering, PdbUnitOrdering.nt_id == PdbCoordinates.id).\
                filter(PdbUnitOrdering.index >= start_index,
                       PdbUnitOrdering.index <= stop_index).\
                filter(PdbCoordinates.pdb == start['pdb'],
                       PdbCoordinates.model == start.get('model', 1),
                       PdbCoordinates.chain == start['chain'])

            return [result.unit_id for result in query]

    def index_of(self, unit):
        PdbUnitOrdering = models.PdbUnitOrdering
        PdbUnitIdCorrespondence = models.PdbUnitIdCorrespondence
        PdbCoordinates = models.PdbCoordinates
        insertion_code = unit['insertion_code'] or ''
        with self.session() as session:
            return session.query(PdbUnitOrdering.index).\
                join(PdbCoordinates, PdbCoordinates.id == PdbUnitOrdering.nt_id).\
                join(PdbUnitIdCorrespondence,
                     PdbUnitIdCorrespondence.old_id == PdbCoordinates.id).\
                filter(PdbCoordinates.pdb == unit['pdb'],
                       PdbCoordinates.model == unit.get('model', 1),
                       PdbCoordinates.chain == unit['chain'],
                       PdbCoordinates.number == unit['number'],
                       PdbCoordinates.ins_code == insertion_code).\
                one().\
                index
