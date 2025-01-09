from langchain_core.output_parsers import PydanticOutputParser
from source.models.structures.journey import ModuleStructure
from source.prompts.actions import structured

module_structured = structured.customize()
module_structured.parser = PydanticOutputParser(pydantic_object=ModuleStructure)
