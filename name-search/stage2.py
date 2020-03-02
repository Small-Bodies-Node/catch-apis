"""
STAGE 2 of Pipeline
Load search terms into DB
"""

import os
from typing import List
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, session as sqSession
from sqlalchemy.dialects.postgresql import insert, dml
from models.name_search import NameSearch, base, EBodyType
from env import ENV

from stage0 import name_search_items_csv_file


#########################
# Build db-connection URI
#########################

# Build db uri
db_engine_URI: str = (
    f"{ENV.DB_DIALECT}://{ENV.DB_USERNAME}:{ENV.DB_PASSWORD}@{ENV.DB_HOST}"
    f"/{ENV.DB_DATABASE}")
db: Engine = create_engine(db_engine_URI, pool_recycle=3600)
# Create tables if not exist
base.metadata.create_all(db)
# Create session
Session = sessionmaker(db)
session: sqSession.Session = Session()

########################################
# Build function to save entries to DB
########################################


def uploadNameSearchInstancesToDB() -> None:

    ################################################################
    # Import search-name data from csv file created in earlier stage
    ################################################################

    # Init list of NameSearch instances
    name_search_items: List[NameSearch] = []

    # Add asteroid data in csv file as NameSearch instances
    with open(name_search_items_csv_file, encoding="utf-8") as content:
        lines = content.readlines()
        for line in lines:
            parts = line.split(',')
            try:
                name_search_items.append(
                    NameSearch(
                        target=parts[0].strip(),
                        comparison_text=parts[1].strip(),
                        display_text=parts[2].strip(),
                        body_type=parts[3].strip()
                    )
                )
            except:
                # Note: Header line will be rejected
                print('Rejected >>> '+str(parts) + '<<<')

    isUpserting = 1  # Toggle between upsert behavior and simple-upload
    for item in name_search_items:
        if isUpserting:
            # Use this for simple insertion; conflicts cause errors
            stmt: dml.Insert = insert(NameSearch).values(
                target=item.target,
                comparison_text=item.comparison_text,
                display_text=item.display_text,
                body_type=item.body_type
            )
            # Use this for updating on conflict
            stmt2: dml.Insert = stmt.on_conflict_do_update(
                constraint='name_search_pkey',  # Get this from `\d small_bodies;`
                set_=dict(
                    comparison_text=item.comparison_text,
                    display_text=item.display_text,
                    body_type=item.body_type
                )
            )
            # Use this for ignoring on conflict
            stmt3: dml.Insert = stmt.on_conflict_do_nothing()
            session.execute(stmt3)
        else:
            session.add(item)

    # Try committing changes; rollback on error
    try:
        session.commit()
    except:
        print("Egregious error invoked!")
        session.rollback()


###################
# Perform uploading
###################

if __name__ == "__main__":
    uploadNameSearchInstancesToDB()
