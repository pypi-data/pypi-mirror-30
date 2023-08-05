"""The module that contains the cecs implementation."""


class World:
    """World class"""

    def __init__(self):
        """A World object keeps track of all Entities, Components and Systems.
        """
        # Entities
        self.current_entity_id = -1
        self.entities = {}
        self.dead_entities = set()
        # Components
        self.components = {}
        self.current_system_id = -1
        # Systems
        self.systems = {}
        self.system_categories = {}

    # Entity functions
    def add_entity(self, *components):
        """Creates a new entity.

        This method creates a new entity in the world, this is just a plain integer.
        You can optionally pass components to be added to the entity.

        :param components: Optional components to be added to the entity.
        :return: The id of the created entity.
        """
        self.current_entity_id += 1
        self.entities[self.current_entity_id] = {}

        for component in components:
            self.add_component(self.current_entity_id, component)

        return self.current_entity_id

    def delete_entity(self, entity, immediate=False):
        """Deletes an entity.

        This method deletes an entity. An entity can be immediately created or can be put on a dead_entity list.
        The entities in the dead_entity list are removed when one of the system process methods is called.

        :param entity: The id of the entity that needs to be deleted.
        :param immediate: If true the entity is immediately deleted.
        """
        if immediate:
            for component_type in self.entities[entity]:
                self.components[component_type].discard(entity)

                if not self.components[component_type]:
                    del self.components[component_type]

            del self.entities[entity]

        else:
            self.dead_entities.add(entity)

    def delete_dead_entities(self):
        """Deletes the entities in the dead_entity list.

        This method deletes all the dead_entities from the World.
        """
        if self.dead_entities:
            for entity in self.dead_entities:
                self.delete_entity(entity, immediate=True)
            self.dead_entities.clear()

    # Component functions
    def get_component_from_entity(self, entity, component_type):
        """Get the component instance of a component type from the entity.

        :param entity: The id of the entity.
        :param component_type: The component type.
        :return: The component instance.
        """
        return self.entities[entity][component_type]

    def get_all_components_from_entity(self, entity):
        """Get all the components from the entity.

        :param entity: The id of the entity.
        :return: Returns all components from the entity as a tuple.
        """
        return tuple(self.entities[entity].values())

    def has_component(self, entity_id, component_type):
        """Checks if the entity has an instance of the given component type.

        :param entity_id: The id of the entity.
        :param component_type: The component type that needs to be checked.
        :return: Returns true if the entity has a component of the component type.
        """
        if entity_id in self.entities:
            if component_type in self.entities[entity_id]:
                return True
        return False

    def add_component(self, entity_id, component_instance):
        """Add a component to the given entity.

        :param entity_id: The id of the entity.
        :param component_instance: The component instance to add.
        """
        if entity_id in self.entities:
            if type(component_instance) not in self.components:
                self.components[type(component_instance)] = set()

            self.components[type(component_instance)].add(entity_id)
            self.entities[entity_id][type(component_instance)] = component_instance

    def remove_component(self, entity_id, component_type):
        """Removes a component from the given entity.

        :param entity_id: The id of the entity.
        :param component_type: The component type to remove.
        """
        self.components[component_type].discard(entity_id)

        if not self.components[component_type]:
            # TODO check the following line for correctness
            del self.components[component_type]

        del self.entities[entity_id][component_type]

        if not self.entities[entity_id]:
            del self.entities[entity_id]

    def get_component(self, component_type):
        """Get all entities with the given component type.

        :param component_type: The component type.
        :return: Iterator on the entities with the given component type as a tuple (entity, component).
        """
        entity_db = self.entities
        for entity in self.components.get(component_type, []):
            yield entity, entity_db[entity][component_type]

    def get_components(self, *component_types):
        """Get all entities with the given component types.

        :param component_types: The component types.
        :return: Iterator on the entities with the given component types as a tuple (enitty, components).
        """
        entity_db = self.entities
        comp_db = self.components

        try:
            for entity in set.intersection(*[comp_db[ct] for ct in component_types]):
                yield entity, [entity_db[entity][ct] for ct in component_types]
        except KeyError:
            pass

    # System functions
    def has_system_category(self, system_category):
        """Checks if the system category is in the world

        :param system_category: The given system category name.
        :return: True if it exists else it returns False.
        """
        return system_category in self.system_categories

    def add_system(self, system_instance, system_category=""):
        """Add a system to the World.

        :param system_instance: The instance of the system.
        :param system_category: The category the system is in.
        :return: The id of the system.
        """
        self.current_system_id += 1
        if system_category not in self.system_categories:
            self.system_categories[system_category] = set()

        self.system_categories[system_category].add(self.current_system_id)
        self.systems[self.current_system_id] = system_instance
        system_instance.world = self
        system_instance.system_category = system_category
        # Initialize the system
        system_instance.initialize()
        return self.current_system_id

    def remove_system(self, system_id):
        """"Remove a system from the World.

        :param system_id: The id of the system that needs to be removed.
        """
        sys = self.systems[system_id]
        cat = sys.system_category

        self.system_categories[cat].discard(system_id)

        if not self.system_categories[cat]:
            del self.system_categories[cat]

        del self.systems[system_id]

    def remove_system_category(self, system_category):
        """Remove a system category from the World.

        :param system_category: The system category that needs to be removed.
        """
        # TODO optimize this and the following line with the list is not satisfactory
        system_category_id_list = list(self.system_categories[system_category])
        for system_id in system_category_id_list:
            self.remove_system(system_id)

    def get_system(self, system_id):
        """"Gets the system that corresponds to the given id.

        :param system_id: The id of the system that needs to be returned.
        """
        return self.systems[system_id]

    def process_systems(self, *system_ids):
        """"Process the given systems.

        :param system_ids: The id of the systems that needs to be processed.
        """
        for system_id in system_ids:
            self.systems[system_id].process()

    def process_system_categories(self, *system_categories):
        """Process the systems in the given categories.

        :param system_categories: The system categories from which all systems need to be processed.
        """
        for system_category in system_categories:
            if system_category in self.system_categories:
                for system_id in self.system_categories[system_category]:
                    self.systems[system_id].process()

    def process_all(self):
        """Process all systems in the World.
        """
        self.delete_dead_entities()

        for system in self.systems.values():
            system.process()


class System:
    """System class"""

    def __init__(self):
        """The initializer of the System.
        """
        self.world = None
        self.system_category = None

    def initialize(self):
        """The initialize method of the system.
        """
        pass

    def process(self):
        """The process method of the system.
        """
        pass