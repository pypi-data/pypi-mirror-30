
import copy

import pandas as pd

from IPython.display import Markdown

from ._util import Util
from sgmarkets_api_auth.util import save_result


class ResponseRotbComputeStrategyPrices:
    """
    TBU
    """

    def __init__(self,
                 li_raw_data=None,
                 obj_req=None):
        """
        """
        msg1 = 'Error: li_raw_data must be a list - Run call_api() again with debug=True'
        msg2 = 'Error: Each dic_res must be a list - Run call_api() again with debug=True'
        msg3 = 'Error: stratedySerie must be a key of each dic_res - Run call_api() again with debug=True'

        assert isinstance(li_raw_data, list), msg1
        for dic_res in li_raw_data:
            assert isinstance(dic_res, dict), msg2
            assert 'strategySerie' in dic_res, msg3

        raw_data = []
        for dic_res in li_raw_data:
            raw_data += dic_res['strategySerie']

        self.raw_data = copy.deepcopy(raw_data)
        self.obj_req = obj_req

        self.df_req, self.df_res = self._build_df_res_req()
        self.dic_req_param, self.dic_res_param = self._build_dic_param()

    def _get_dates(self, df_res):
        """
        """
        dic = self.obj_req.df_top.to_dict()
        dic = dic['Value']

        if 'dates' in dic:
            res = dic['dates'].replace("'", '"')
            return json.loads(res)
            
        return Util.get_unique_list(df_res['date'])

    def _build_df_res_req(self):
        """
        """
        # df_res (response)
        li_data = [f for f in self.raw_data]

        for e in li_data:
            if 'greeks' in e:
                for greek in ['delta', 'gamma', 'vega', 'theta']:
                    e[greek] = e['greeks'][greek]
                e.pop('greeks')
        df_res = pd.DataFrame(li_data)

        # build list of dates
        li_date = self._get_dates(df_res)
        N = len(li_date)

        # df_req (request)
        # duplicate df_leg by number of dates
        df_leg = self.obj_req.df_leg
        df_req = pd.concat([df_leg] * N,
                           axis=0).reset_index(drop=True)

        # reorder results by date then initial order (tag)
        df_res['tag'] = range(len(df_res))
        df_res = df_res.sort_values(['date', 'tag']).reset_index(drop=True)

        # move date from df_res to df_req (more natural)
        df_req['date'] = pd.to_datetime(df_res['date'].copy())
        df_res = df_res.drop('date', axis=1)

        # join df_req and df_res to make df_set
        df_res.index = df_req["date"].iloc[0:N]

        return df_req, df_res

    def _build_dic_param(self):
        """
        """
        dic_req = self.df_req.to_dict()
        dic_req_param = {k: Util.get_unique_list(v.values())
                         for k, v in dic_req.items()}

        dic_data = self.df_res.to_dict()
        dic_res_param = {k: Util.get_unique_list(v.values())
                         for k, v in dic_data.items()}

        return dic_req_param, dic_res_param

    def save(self,
             folder_save='dump',
             name=None,
             tagged=True,
             excel=False):
        """ 
        Split save for strategyprice type since no df.set in the object
        """
        if name is None:
            name = 'SG_Research_ROTB'

        save_result(self.df_res,
                    folder_save,
                    name=name + 'Strategy_res',
                    tagged=tagged,
                    excel=excel)

        save_result(self.df_req,
                    folder_save,
                    name=name + 'Strategy_req',
                    tagged=tagged,
                    excel=excel)

    def _repr_html_(self):
        """
        """
        return self.df_res.to_html()

    def info(self):
        """
        """
        md = """
A PostprocessROTB object from ComputeStrategyPrices endpoint has the properties:
+ `df_req`: request data (dataframe)
+ `df_res`: response data (dataframe)


+ `dic_req_param`: params in request, each param contains a list of all values taken (dictionary)
+ `dic_res_param`: params in response, each param contains a list of all values taken (dictionary)

+ `raw_data`: raw data in response under key 'componentSeries' (dictionary)

and the methods:
+ `save()` to save the data as `.csv` and `.xlsx` files
        """
        return Markdown(md)
