import { MEDDataObject } from "../../components/workspace/NewMedDataObject"
import { recursivelyRecenseWorkspaceTree } from "./workspaceUtils"
import { collectionExists, connectToMongoDB, insertMEDDataObjectIfNotExists } from "../../components/mongoDB/mongoDBUtils"

/**
 * @description Used to update the data present in the DB with local files not present in the database
 * @param {Object} workspaceObject
 */
export const updateGlobalData = async (workspaceObject) => {
  let rootChildren = workspaceObject.workingDirectory.children
  let rootParentID = "ROOT"
  let rootName = workspaceObject.workingDirectory.name
  let rootType = "directory"
  let rootPath = workspaceObject.workingDirectory.path
  let rootDataObject = new MEDDataObject({
    id: rootParentID,
    name: rootName,
    type: rootType,
    parentID: null,
    childrenIDs: [],
    inWorkspace: true,
    path: rootPath,
    isLocked: false,
    usedIn: null
  })
  await insertMEDDataObjectIfNotExists(rootDataObject, rootPath)
  await recursivelyRecenseWorkspaceTree(rootChildren, rootParentID)
}

/**
 * @descritption load the MEDDataObjects from the MongoDB database
 * @returns medDataObjectsDict dict containing the MEDDataObjects in the Database
 */
export async function loadMEDDataObjects() {
  let medDataObjectsDict = {}
  try {
    // Get global data
    const fs = require("fs")
    const db = await connectToMongoDB()
    const collection = db.collection("medDataObjects")
    const medDataObjectsArray = await collection.find().toArray()
    // Format data
    for (const data of medDataObjectsArray) {
      const medDataObject = new MEDDataObject(data)
      // Check if local objects still exist
      if (medDataObject.inWorkspace && medDataObject.path) {
        try {
          fs.accessSync(medDataObject.path)
          medDataObjectsDict[medDataObject.id] = medDataObject
        } catch (error) {
          // Check if collection exists
          const collectionExistsCheck = await collectionExists(medDataObject.id)
          if (!collectionExistsCheck) {
            // Remove from database
            collection.deleteOne({ id: medDataObject.id }).then(() => {
              console.log(`MEDDataObject with id ${medDataObject.id} removed from database as it no longer exists locally`)
            }).catch((deleteError) => {              
              console.error(`Failed to remove MEDDataObject with id ${medDataObject.id} from database: `, deleteError)
            })
          } else {
            console.error(`${medDataObject.name}: not found locally, path will be set to null`, medDataObject)
            medDataObject.path = null
            medDataObject.inWorkspace = false
            medDataObjectsDict[medDataObject.id] = medDataObject

            // Update database
            collection.updateOne(
              { id: medDataObject.id },
              { $set: { path: null, inWorkspace: false } }
            ).then(() => {
              console.log(`Database updated for MEDDataObject with id ${medDataObject.id}: path set to null and inWorkspace set to false`)
            }).catch((updateError) => {
              console.error(`Failed to update MEDDataObject with id ${medDataObject.id} in database: `, updateError)
            })
          }
        }
      } else {
        medDataObjectsDict[medDataObject.id] = medDataObject
      }
    }
  } catch (error) {
    console.error("Failed to load MEDDataObjects: ", error)
  }
  return medDataObjectsDict
}
