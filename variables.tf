variable "prefix" {
  description = "A prefix for all the resource"
}
variable "tag_filter" {
  description = "A tag to select the image to delete"
  default = "AnsibleImageOriginId"
}
variable "exclusion_tag" {
  description = "Tag that if it is True block the image to be deleted"
  default = "DoNotDelete"
}
