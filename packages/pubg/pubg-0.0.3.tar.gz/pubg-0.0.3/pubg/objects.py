class Base:
    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.__dict__}>'


class Match(Base):
    def __init__(self, data):
        super().__init__(data)
        self.id = self.data.get('id')
        self.created_at = self.data.get('createdAt')
        self.duration = self.data.get('duration')
        self.rosters = self.roster_list()
        # rounds
        self.assets = self.asset_list()
        # spectators
        # stats
        self.game_mode = self.data.get('gameMode')
        self.patch_version = self.data.get('patchVersion')
        self.title_id = self.data.get('titleId')
        self.shard_id = self.data.get('shardId')
        # tags

    def roster_list(self):
        return [Roster(data) for data in self.data.get('rosters')]

    def asset_list(self):
        return [Asset(data) for data in self.data.get('assets')]


class Roster(Base):
    def __init__(self, data):
        super().__init__(data)
        self.id = self.data.get('id')
        # team
        self.participants = self.participant_list()
        # stats
        self.won = self.data.get('won')
        self.shard_id = self.data.get('shardId')

    def participant_list(self):
        return [Participant(data) for data in self.data.get('participants')]


class Asset(Base):
    def __init__(self, data):
        super().__init__(data)
        self.id = self.data.get('id')
        self.title_id = self.data.get('titleId')
        self.shard_id = self.data.get('shardId')
        self.name = self.data.get('name')
        self.description = self.data.get('description')
        self.created_at = self.data.get('createdAt')
        self.filename = self.data.get('filename')
        self.content_type = self.data.get('contentType')
        self.url = self.data.get('URL')


class Participant(Base):
    def __init__(self, data):
        super().__init__(data)
        self.id = self.data.get('id')
        # stats
        self.actor = self.data.get('actor')
        self.shard_id = self.data.get('shardId')


class Status(Base):
    def __init__(self, data):
        super().__init__(data)
        self.id = self.data.get('data').get('id')
        self.released_at = self.data.get('data').get('attributes').get('releasedAt')
        self.version = self.data.get('data').get('attributes').get('version')
