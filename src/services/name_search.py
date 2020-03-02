"""
    Name-search functionality
"""

from typing import List
from .database_provider import data_provider_session, Session, db_engine
from models.name_search import base
from .query import TargetTypePatterns


# Create NameSearch table if not exists; make db aware of this model
base.metadata.create_all(db_engine)


def name_search(search_submission: str) -> List:
    """
        Function to query DB for fuzzy name search
    """
    found_names: List = []

    # Clean up search_submission

    session: Session
    with data_provider_session() as session:

        q = session.execute(

            #
            # Injection-prone query:
            #
            # f"""
            #     SELECT target_text, search_text, body_type FROM name_search
            #     ORDER BY (search_text <-> '{search_submission}')
            #     LIMIT 10;
            # """

            #
            # Injection-safe query preparation:
            #
            f"""
                PREPARE nameSearchPlan (text) AS
                    SELECT * FROM name_search
                    ORDER BY (name_search.comparison_text <-> $1)
                    LIMIT 10;
                -- EXECUTE fooplan('{search_submission}');
            """
        )

        r = session.execute(
            #
            # Injection-safe query execution:
            #
            f"""
                EXECUTE nameSearchPlan('{search_submission}');
            """
        )

        s = session.execute(
            #
            # Injection-safe query ridiculous final step:
            #
            f"""
                DEALLOCATE nameSearchPlan;
            """
        )

        print("<><><><><>")
        for p in r:
            print(p)
            found_names.append(
                {
                    "target": p[0],
                    "comparison_text": p[1],
                    "display_text": p[2],
                    "body_type": p[3],
                }
            )

        print("**********")
        print(found_names)
        print(found_names[0])

    return found_names
