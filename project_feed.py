from typing import Optional, Text, List
from threading import Lock

import logging
import os
import json

from portfolio.models import Project

class ProjectFeedNotInitialisedException(Exception):
    pass

class InvalidPathException(Exception):
    pass

class ProjectFeed:
    ''' Provides access to a feed of projects. '''

    def __init__(self):
        self.projects: List[Project] = []      
        self.path: Optional[Text] = None
        self.loading_lock = Lock()
        self.loaded: bool = False
        self.initialised = False

    def initialise(self, path: Text):
        self.path = path        
        self.initialised = True

    def get_feed(self) -> List[Project]:
        ''' Gets the collection of projects in the feed. '''
        self.check_loaded()

        return self.projects

    def check_loaded(self): 
        if not self.initialised:
            raise ProjectFeedNotInitialisedException('Project feed must first be initialised.')

        if not self.loaded:
            self._load()

    def _load(self):
        with self.loading_lock:
            if self.loaded:
                # Another thread has loaded the posts while waiting for the lock so there's nothing to do.
                return

            logging.debug('Loading project feed from {}'.format(self.path))

            if not os.path.exists(self.path):
                # The path given for searching for blog posts does not exist, so throw an early error.
                raise InvalidPathException('Supplied path for project feed does not exist - {}'.format(self.path))

            with open(self.path) as f:
                projects = list(map(self.create_project, json.load(f)))

                self.projects = projects

                logging.debug('Loaded {} projects into project feed'.format(len(self.projects)))

            self.loaded = True

    def create_project(self, data: str) -> Project:
        return Project(data['project_id'], data['name'], data['description'], data['link'], data['link_description'])

project_feed_manager = ProjectFeed()
