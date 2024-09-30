from .communityImport import import_community_parquet
from .communityReportImport import import_community_report_parquet
from .documentImport import import_document_parquet
from .entityImport import import_entity_parquet
from .entityRelationImport import import_entity_relation_parquet
from .uintFileImport import import_unit_file_parquet


async def import_parquet_files():
    result = ""
    docummentImportedResult = await import_document_parquet()
    result += "\n" + f"Imported document parquet files successfully,records imported: {docummentImportedResult}"
    unitFileImportedResult = await import_unit_file_parquet()
    result += "\n" + f"Imported unit file parquet files successfully,records imported: {unitFileImportedResult}"
    entityImportedResult = await import_entity_parquet()
    result += "\n" + f"Imported entity file parquet files successfully,records imported: {entityImportedResult}"
    entityRelationImportedResult = await import_entity_relation_parquet()
    result += "\n" + f"Imported entity relation file parquet files successfully,records imported: {entityRelationImportedResult}"
    communityImportedResult = await import_community_parquet()
    result += "\n" + f"Imported community file parquet files successfully,records imported: {communityImportedResult}"
    communityReportImportedResult = await import_community_report_parquet()
    result += "\n" + f"Imported community report file parquet files successfully,records imported: {communityReportImportedResult}"
    return result