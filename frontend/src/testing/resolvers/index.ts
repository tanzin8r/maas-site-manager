import { authResolvers } from "./auth";
import { enrollmentRequestsResolvers } from "./enrollmentRequests";
import { imagesResolvers } from "./images";
import { sitesResolvers } from "./sites";
import { tileHandler } from "./tiles";
import { tokensResolvers } from "./tokens";
import { usersResolvers } from "./users";
export const allResolvers = [
  authResolvers.login.handler(),
  enrollmentRequestsResolvers.listEnrollmentRequests.handler(),
  enrollmentRequestsResolvers.postEnrollmentRequests.handler(),
  imagesResolvers.listUpstreamImages.handler(),
  imagesResolvers.getImageSource.handler(),
  imagesResolvers.updateUpstreamImageSource.handler(),
  imagesResolvers.selectUpstreamImages.handler(),
  imagesResolvers.deleteImages.handler(),
  imagesResolvers.uploadImage.handler(),
  imagesResolvers.listImages.handler(),
  sitesResolvers.listSites.handler(),
  sitesResolvers.sitesCoordinates.handler(),
  sitesResolvers.getSite.handler(),
  sitesResolvers.deleteSites.handler(),
  sitesResolvers.updateSites.handler(),
  tileHandler,
  tokensResolvers.listTokens.handler(),
  tokensResolvers.deleteTokens.handler(),
  tokensResolvers.createTokens.handler(),
  tokensResolvers.exportTokens.handler(),
  usersResolvers.listUsers.handler(),
  usersResolvers.getUser.handler(),
  usersResolvers.updateUser.handler(),
  usersResolvers.getCurrentUser.handler(),
  usersResolvers.updateCurrentUser.handler(),
  usersResolvers.updateCurrentUserPassword.handler(),
  usersResolvers.deleteUser.handler(),
  usersResolvers.createUser.handler(),
];
