# A plugin to enable linking by ID (i.e. join_on_key).

from glue.config import link_helper
from glue.core.link_helpers import LinkCollection
from glue.core.component_link import KeyLink


__all__ = ["Index_Link"]

# based on https://sourcegraph.com/github.com/glue-viz/glue/-/blob/glue/plugins/coordinate_helpers/link_helpers.py?L42:33

@link_helper(category="Link by ID")
class Index_Link(LinkCollection):
    # inherit from linkCollection to skip this line https://github.com/glue-viz/glue/blob/5a878451a1636b141a687a482239a37287a32198/glue/config.py#L790
    cid_independent = False

    display = "Link by ID/Index"
    description = "Link two datasets by a common ID or Index (for example, if two datasets have the same experiment ID)"

    labels1 = ["ID in dataset 1"]
    labels2 = ["ID in dataset 2"]

    def __init__(self, *args, cids1=None, cids2=None, data1=None, data2=None):
        # only support linking by one value now, even though link_by_value supports multiple
        assert len(cids1) == 1
        assert len(cids2) == 1

        self.data1 = data1
        self.data2 = data2
        self.cids1 = cids1
        self.cids2 = cids2

        data1.join_on_key(data2, cids1[0], cids2[0])
        
        self._links = []
        #self._links = [KeyLink()]
