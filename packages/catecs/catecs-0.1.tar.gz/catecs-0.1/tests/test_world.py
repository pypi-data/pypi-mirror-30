import catecs
import pytest


# Fixtures
@pytest.fixture
def world():
    return catecs.World()


@pytest.fixture
def populate_world():
    pop_world = world()


# Tests
def test_world_instantiation(world):
    assert type(world) is catecs.World
    assert type(world.current_entity_id) is int
    assert type(world.current_system_id) is int
    assert type(world.entities) is dict
    assert type(world.dead_entities) is set
    assert type(world.components) is dict
    assert type(world.systems) is dict
    assert type(world.system_categories) is dict


def test_create_entity(world):
    entity1 = world.add_entity()
    entity2 = world.add_entity()
    assert type(entity1) and type(entity2) is int
    assert entity1 < entity2


def test_create_entity_with_component(world):
    entity1 = world.add_entity(ComponentA())
    entity2 = world.add_entity(ComponentB())
    assert world.has_component(entity1, ComponentA) is True
    assert world.has_component(entity1, ComponentB) is False
    assert world.has_component(entity2, ComponentA) is False
    assert world.has_component(entity2, ComponentB) is True


def test_delete_entity_immediate(world):
    entity1 = world.add_entity()
    world.add_component(entity1, ComponentA())
    entity2 = world.add_entity()
    world.add_component(entity2, ComponentB())
    entity3 = world.add_entity()
    # Entity 2 with components
    assert entity2 == 1
    world.delete_entity(entity2, immediate=True)
    with pytest.raises(KeyError):
        world.get_all_components_from_entity(entity2)
    # Entity 3 without components
    assert entity3 == 2
    world.delete_entity(entity3, immediate=True)
    with pytest.raises(KeyError):
        world.get_all_components_from_entity(entity3)
    # Delete an entity that doesn't exist
    with pytest.raises(KeyError):
        world.delete_entity(999, immediate=True)


def test_delete_entity_not_immediate(world):
    entity1 = world.add_entity()
    world.add_component(entity1, ComponentA())
    # Process all
    assert entity1 == 0
    world.delete_entity(entity1)
    world.delete_dead_entities()
    with pytest.raises(KeyError):
        world.get_all_components_from_entity(entity1)


def test_get_component_from_entity(world):
    entity = world.add_entity()
    world.add_component(entity, ComponentA())
    assert isinstance(world.get_component_from_entity(entity, ComponentA), ComponentA)
    with pytest.raises(KeyError):
        world.get_component_from_entity(entity, ComponentB)


def get_all_components_from_entity(world):
    entity = world.add_entity()
    world.add_component(entity, ComponentA())
    world.add_component(entity, ComponentB())
    world.add_component(entity, ComponentC())
    all_components = world.get_all_components_from_entity(entity)
    assert type(all_components) is tuple
    assert len(all_components) == 3
    with pytest.raises(KeyError):
        world.get_all_components_from_entity(999)


def test_has_component(world):
    entity1 = world.add_entity()
    entity2 = world.add_entity()
    world.add_component(entity1, ComponentA())
    world.add_component(entity2, ComponentB())
    assert world.has_component(entity1, ComponentA) is True
    assert world.has_component(entity1, ComponentB) is False
    assert world.has_component(entity2, ComponentA) is False
    assert world.has_component(entity2, ComponentB) is True


def test_get_component(world):
    component_instance = ComponentA()
    entity_id = world.add_entity(component_instance)
    for get_entity_id, get_component_instance in world.get_component(ComponentA):
        assert entity_id is get_entity_id
        assert component_instance is get_component_instance


def test_get_two_components(world):
    assert False
    # TODO implement the test


def test_get_three_components(world):
    assert False
    # TODO implement the test


def test_has_system_category(world):
    system_a = SystemA()
    assert world.has_system_category("test") is False
    world.add_system(system_a, "test")
    assert world.has_system_category("test")


def test_add_system_without_system_categories(world):
    system_a = SystemA()
    assert isinstance(system_a, catecs.System)
    world.add_system(system_a)
    assert len(world.systems) == 1
    assert isinstance(world.systems[0], catecs.System)


def test_add_system_with_system_categories(world):
    # Test the correctness of adding system categories
    system_a_id = world.add_system(SystemA(), "test_1")
    system_b_id = world.add_system(SystemA(), "test_2")
    world.add_system(SystemA(), "test_2")
    assert len(world.systems) == 3
    assert world.has_system_category("test_1")
    assert world.get_system(system_a_id).system_category != world.get_system(system_b_id).system_category


def test_initialize_system(world):
    # Test the initialization of the system
    system_instance = SystemA()
    assert system_instance.a == 1
    system_id = world.add_system(system_instance)
    assert world.get_system(system_id).a == 2


def test_remove_system(world):
    system_id = world.add_system(SystemA(), "test")
    # Remove the system and check if everything went correctly
    world.remove_system(system_id)
    with pytest.raises(KeyError):
        world.get_system(system_id)
    assert world.has_system_category("test") is False


def test_remove_system_category(world):
    world.add_system(SystemA(), "test_1")
    world.add_system(SystemA(), "test_2")
    world.add_system(SystemA(), "test_2")
    # Tests after removal of the system category
    world.remove_system_category("test_2")
    assert world.has_system_category("test_2") is False
    assert len(world.systems) == 1


def test_get_system(world):
    system_id = world.add_system(SystemA())
    assert isinstance(world.get_system(system_id), SystemA)
    with pytest.raises(KeyError):
        world.get_system(system_id + 1)


# TODO add tests for the process system functions


# Helper classes and functions
class ComponentA:
    def __init__(self):
        self.a = -1.0
        self.b = 2.0


class ComponentB:
    def __init__(self):
        self.a = True
        self.b = False


class ComponentC:
    def __init__(self):
        self.a = True
        self.b = 0.5


class SystemA(catecs.System):
    def __init__(self):
        self.a = 1
        super().__init__()

    def initialize(self):
        self.a = 2

    def process(self):
        pass