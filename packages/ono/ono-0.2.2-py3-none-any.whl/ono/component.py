# -*- coding: utf-8 -*-

### imports ###################################################################
import calendar
cal_dict = dict((v, k) for k, v in enumerate(calendar.month_abbr))

import datetime
import logging

###############################################################################
class Component(object):
    def __init__(self, parent):
        self.logger = logging.getLogger('bruker')
        
        self.id_dict = {'no error': 'NOERR'}
        self.host = parent.host
        self.parent = parent
        self.parent_name = parent.name
        self.session = parent.session
        self.status = ''
        self.url_root = parent.url_root
        self.url_diag = ''

    def extract_date(self):
        date_id = self.id_dict['date']
        result = self.parent.find_id(date_id).replace('since ', '')
        
        result_list = result.split(' ')
        day = int(result_list[1])
        month = cal_dict[result_list[2]]
        year = int(result_list[3])
        time = result_list[4]
        
        hour, minute, second = map(int, time.split(':'))
        
        self.date = datetime.datetime(year, month, day)

        self.logger.debug(
                "%s: %s runnig since: %s",
                self.parent_name, self.name, self.date)

    def extract_device_id(self):
        self.device_id = self.parent.find_id(self.id_dict['device_id'])

        self.logger.debug(
                '%s: %s id: %s', self.parent_name, self.name, self.device_id)

    def extract_error(self):
        # error message
        self.error_msg = self.parent.find_id('NOERR')
        
        if self.error_msg != 'No error':                             
            self.logger.error('%s error: %s', self.name, self.error_msg)

        return self.error_msg

    def extract_id(self, id_str):
        value = self.diag_soup.find(id=id_str)
        
        result = ''
        
        if value:
            result = value.string
        else:
            self.logger.warning(
                    '%s warning: Could not extract %s',
                    self.name,
                    id_str)
            
        return result


    def extract_status(self):
        status_id = self.id_dict['status']
        self.status = self.extract_id(status_id).upper()

        self.logger.debug(
                '%s: %s status: %s', self.parent_name, self.name, self.status)


    def extract_type(self):
        type_id = self.id_dict['type']
        self.component_type = self.extract_id(type_id)
        
        self.logger.debug(
                '%s: %s type: %s',
                self.parent_name, self.name, self.component_type)


    def extract_total_run_time(self):
        result = self.extract_id(self.id_dict['total run time'])
        result_list = [r.replace(',', '') for r in result.split(' ')]

        days = hours = minutes = 0

        for d in ['day', 'days']:
            if d in result_list:
                i = result_list.index(d)
                days = int(result_list[i-1])
                break

        for h in ['hour', 'hours']:
            if h in result_list:
                i = result_list.index(h)
                hours = int(result_list[i-1])
                break

        if 'mn' in result_list:
            i = result_list.index('mn')
            minutes = int(result_list[i-1])

        self.total_run_time = datetime.timedelta(
                days=days, hours=hours, minutes=minutes)
        
        self.logger.debug(
                "%s: %s total run time: %s",
                self.parent_name, self.name, self.total_run_time)

    def get_ctrler_config(self):
        for key, web_key in self.cfg_dict.items():
            value = self.parent.ctrler_cfg_dict.pop(web_key)
            setattr(self, key, value)

    def get_config(self):
        for key, web_key in self.cfg_dict.items():
            value = self.parent.web_cfg_dict.pop(web_key)
            setattr(self, key, value)

    def get_diagnostics(self):
        self.diag_soup = self.parent.get_soup(self.url_diag)
