###############################################################################
#
#   Agora Portfolio & Risk Management System
#
#   Copyright 2015 Carlo Sbraccia
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
###############################################################################

from onyx.core import Structure, CurveIntersect, CurveSum
from onyx.core import CreateInMemory, ValueType, ListField
from onyx.core import DiscardInheritedAttribute

from agora.system.ufo_portfolio import Portfolio
from agora.risk.core_functions import WithRiskValueTypes

__all__ = ["FundGroup"]


###############################################################################
@WithRiskValueTypes
@DiscardInheritedAttribute(["Children"])
class FundGroup(Portfolio):
    """
    Class used to represent a group of Funds. FundGroup is a subclass
    of Portfolio and its children are all the underlying funds.
    """
    Funds = ListField()

    # -------------------------------------------------------------------------
    @ValueType()
    def Children(self, graph):
        kids = {fund: 1 for fund in graph(self, "Funds")}
        return Structure(kids)

    # -------------------------------------------------------------------------
    @ValueType()
    def Nav(self, graph):
        funds = graph(self, "Funds")
        group_ccy = graph(self, "Denominated")
        return sum_values("Nav", funds, group_ccy, graph)

    # -------------------------------------------------------------------------
    @ValueType()
    def Gav(self, graph):
        funds = graph(self, "Funds")
        group_ccy = graph(self, "Denominated")
        return sum_values("Gav", funds, group_ccy, graph)

    # -------------------------------------------------------------------------
    @ValueType()
    def Aum(self, graph):
        funds = graph(self, "Funds")
        group_ccy = graph(self, "Denominated")
        return sum_values("Aum", funds, group_ccy, graph)

    # -------------------------------------------------------------------------
    @ValueType("PropSubGraph")
    def NavCurve(self, graph, start=None, end=None):
        funds = graph(self, "Funds")
        group_ccy = graph(self, "Denominated")
        return sum_curves("NavCurve", start, end, funds, group_ccy, graph)

    # -------------------------------------------------------------------------
    @ValueType("PropSubGraph")
    def GavCurve(self, graph, start=None, end=None):
        funds = graph(self, "Funds")
        group_ccy = graph(self, "Denominated")
        return sum_curves("GavCurve", start, end, funds, group_ccy, graph)

    # -------------------------------------------------------------------------
    @ValueType("PropSubGraph")
    def AumCurve(self, graph, start=None, end=None):
        funds = graph(self, "Funds")
        group_ccy = graph(self, "Denominated")
        return sum_curves("AumCurve", start, end, funds, group_ccy, graph)

    # -------------------------------------------------------------------------
    @ValueType("PropSubGraph")
    def PortfolioBy(self, graph, key=None, value=None):
        children = Structure()
        for fund in graph(self, "Funds"):
            port = graph(fund, "PortfolioBy", key=key, value=value)
            children += Structure({port: 1.0})

        name = "Tmp {0:s} - {1:s}".format(self.Name, value)
        ccy = graph(self, "Denominated")
        port = Portfolio(Name=name, Denominated=ccy, Children=children)
        port = CreateInMemory(port)

        return port.Name

    # -------------------------------------------------------------------------
    @ValueType("PropSubGraph")
    def FilteredChildren(self, graph, target=None, level=0):
        kids = Structure()
        for fund in graph(self, "Funds"):
            kids += graph(fund, "FilteredChildren", target=target, level=level)

        return kids

    # -------------------------------------------------------------------------
    @ValueType("PropSubGraph")
    def Aggregate(self, graph, target=None, level=0):
        kids = graph(self, "FilteredChildren", target=target, level=level)
        name = "Tmp {0:s} - {1:s}".format(self.Name, target)
        ccy = graph(self, "Denominated")
        port = Portfolio(Name=name, Denominated=ccy, Children=kids)
        port = CreateInMemory(port)
        return port.Name

# -----------------------------------------------------------------------------
def sum_values(attr, funds, group_ccy, graph):
    group2usd = graph("{0:3s}/USD".format(group_ccy), "Spot")

    total = 0.0
    for fund in funds:
        cross = "{0:3s}/USD".format(graph(fund, "Denominated"))
        ccy2usd = graph(cross, "Spot")
        total += graph(fund, attr) * ccy2usd

    return total / group2usd   


# -----------------------------------------------------------------------------
def sum_curves(attr, start, end, funds, group_ccy, graph):
    cross = "{0:3s}/USD".format(group_ccy)
    group2usd = graph(cross, "GetCurve", start=start, end=end)

    crvs = []
    for fund in funds:
        cross = "{0:3s}/USD".format(graph(fund, "Denominated"))
        ccy2usd = graph(cross, "GetCurve", start=start, end=end)
        crv = graph(fund, attr, start=start, end=end)
        ccy2usd, crv = CurveIntersect([ccy2usd, crv])
        crvs.append(crv*ccy2usd)

    total = CurveSum(crvs)
    group2usd, total = CurveIntersect([group2usd, total])

    return total / group2usd


# -----------------------------------------------------------------------------
def prepare_for_test():
    pass

