from odoo import fields, http, models, _
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.tools import consteq
from odoo.tools.image import image_data_uri

from werkzeug.wsgi import get_current_url



class InterviewEvaluation(http.Controller):
    @http.route(['/evaluation/form/'], type='http', auth="user", website=True)
    def evaluation_form(self,  **kw):
        uid = request.session.uid

        if kw.get('users'):
            users = kw.get('users').split(',')
            user_ids = users
            if not str(uid) in user_ids:
                return request.render("instellars_interview_schedule.not_authorised", {})
        else:
            return request.render("instellars_interview_schedule.not_authorised", {})



        if not kw.get('applicant_id'):
            return request.render(
                'website.http_error',
                {'status_code': 'Oops',
                 'status_message': 'The employee is not linked to an existing user, please contact the administrator..'})

        values = {}


        applicant_id = False       
        stage_id = False
        appl = request.env['hr.applicant'].sudo().search([('id','=',int(kw.get('applicant_id')))])

        if appl.stage_id.tech1_interview_feedback_enable == True:
            if appl.tech1_interview:
                return request.render("instellars_interview_schedule.evaluation_submit_thank_you", {
                'stage_name': appl.stage_id.name,'applicant_name':appl.partner_name})
        elif appl.stage_id.tech2_interview_feedback_enable == True:
            if appl.tech2_interview:
                return request.render("instellars_interview_schedule.evaluation_submit_thank_you", {
                'stage_name': appl.stage_id.name,'applicant_name':appl.partner_name})
        elif appl.stage_id.managerial_interview_feedback_enable == True:
            if appl.managerial_interview:
                return request.render("instellars_interview_schedule.evaluation_submit_thank_you", {
                'stage_name': appl.stage_id.name,'applicant_name':appl.partner_name})
         

        if  not(appl.stage_id.tech1_interview_feedback_enable  or appl.stage_id.tech2_interview_feedback_enable or appl.stage_id.managerial_interview_feedback_enable):
            return request.render("instellars_interview_schedule.not_tech_interview_stage", {'stage_name': appl.stage_id.name})


        for field_name, value in kw.items():
            if field_name == 'stage_id':
                stage_id = value
            elif field_name == 'applicant_id':
                applicant_id = value
            else:
                old_value = ""

        stage = request.env['hr.recruitment.stage'].sudo().search([('id','=',int(kw.get('stage_id')))]) 


        values.update({
            'applicant_id': applicant_id,
            'applicant_name':appl.partner_name, 
            'application_data':appl,
            'stage_id': stage_id,
            'stage_name': stage.name,
            'stage':stage,
            'original_link': get_current_url(request.httprequest.environ)})

        if appl.resume_upload:
            pdf_src = "data:application/pdf;base64,%s" % (appl.resume_upload.decode())
            # pdf_src = image_data_uri(appl.igc_resume)

            attachment = request.env['ir.attachment'].sudo().search([('res_model','=','hr.applicant'),('res_id','=',applicant_id),('res_field','=','resume_upload')])
            values.update({
            'attachment': attachment, 
            'pdf_src':pdf_src,          

                })
        
        if appl.stage_id.tech1_interview_feedback_enable == True or appl.stage_id.tech2_interview_feedback_enable == True:
            response = request.render("instellars_interview_schedule.interview_evaluation", values)
        else:
            response = request.render("instellars_interview_schedule.managerial_interview_evaluation", values)
        response.flatten()
        return response



    @http.route(['/evaluation/thank_you/<int:applicant_id>'], type='http', auth="public", website=True)
    def evaluation_submit_thank_you(self, applicant_id=None, **kw):
        applicant = request.env['hr.applicant'].sudo().browse(applicant_id)
        
        return request.render("instellars_interview_schedule.evaluation_submit_thank_you", {
            'stage_name': applicant.stage_id.name,'applicant_name':applicant.partner_name})

    def update_evaluation_info(self,  advantages, **kw):
        # Generate a new contract with the current modifications
        tech1_feedback = advantages['personal_info']
        if tech1_feedback['kanban_state'] == 'hold':
            reason = tech1_feedback['hold_reason']
            ks = 'Hold'
        elif tech1_feedback['kanban_state'] == 'blocked':
            reason = tech1_feedback['reject_reason']
            ks = 'Blocked'
        elif tech1_feedback['kanban_state'] == 're_schedule':
            reason = tech1_feedback['re_schedule_reason']
            ks = 'Re Scheduled'
        else:
            reason = ''
            ks = 'Selected For Next Round'

        tech1_data = {
                        'ques1_tech1': tech1_feedback['ques1_tech1'] or ' ',
                        'ques1_tech1_cmnt': tech1_feedback['ques1_tech1_cmnt'] or ' ',
                        'ques2_tech1': tech1_feedback['ques2_tech1'] or ' ',
                        'ques2_tech1_cmnt': tech1_feedback['ques2_tech1_cmnt'] or ' ',
                        'ques3_tech1': tech1_feedback['ques3_tech1'] or ' ',
                        'ques3_tech1_cmnt': tech1_feedback['ques3_tech1_cmnt'] or ' ',
                        'ques4_tech1': tech1_feedback['ques4_tech1'] or ' ',
                        'ques4_tech1_cmnt': tech1_feedback['ques4_tech1_cmnt'] or ' ',
                        'ques5_tech1': tech1_feedback['ques5_tech1'] or ' ',
                        'ques5_tech1_cmnt': tech1_feedback['ques5_tech1_cmnt'] or ' ',
                        'ques6_tech1': tech1_feedback['ques6_tech1'] or ' ',
                        'ques6_tech1_cmnt': tech1_feedback['ques6_tech1_cmnt'] or ' ',
                        'ques7_tech1': tech1_feedback['ques7_tech1'] or ' ',
                        'ques7_tech1_cmnt': tech1_feedback['ques7_tech1_cmnt'] or ' ',
                        'ques8_tech1': tech1_feedback['ques8_tech1'] or ' ',
                        'ques8_tech1_cmnt': tech1_feedback['ques8_tech1_cmnt'] or ' ',
                        'ques9_tech1': tech1_feedback['ques9_tech1'] or ' ',
                        'ques9_tech1_cmnt': tech1_feedback['ques9_tech1_cmnt'] or ' ',
                        'ques10_tech1': tech1_feedback['ques10_tech1'] or ' ',
                        'ques10_tech1_cmnt': tech1_feedback['ques10_tech1_cmnt'] or ' ',
                        'ques11_tech1': tech1_feedback['ques11_tech1'] or ' ',
                        'ques11_tech1_cmnt': tech1_feedback['ques11_tech1_cmnt'] or ' ',
                        'ques12_tech1': tech1_feedback['ques12_tech1'] or ' ',
                        'ques12_tech1_cmnt': tech1_feedback['ques12_tech1_cmnt'] or ' ',
                        'ques13_tech1': tech1_feedback['ques13_tech1'] or ' ',
                        'ques13_tech1_cmnt': tech1_feedback['ques13_tech1_cmnt'] or ' ',
                        'ques14_tech1': tech1_feedback['ques14_tech1'] or ' ',
                        'ques14_tech1_cmnt': tech1_feedback['ques14_tech1_cmnt'] or ' ',
                        'ques15_tech1': tech1_feedback['ques15_tech1'] or ' ',
                        'ques15_tech1_cmnt': tech1_feedback['ques15_tech1_cmnt'] or ' ',
                        'ques16_tech1': tech1_feedback['ques16_tech1'] or ' ',
                        'ques16_tech1_cmnt': tech1_feedback['ques16_tech1_cmnt'] or ' ',
                        'ques17_tech1': tech1_feedback['ques17_tech1'] or ' ',
                        'ques17_tech1_cmnt': tech1_feedback['ques17_tech1_cmnt'] or ' ',
                        'ques18_tech1': tech1_feedback['ques18_tech1'] or ' ',
                        'ques18_tech1_cmnt': tech1_feedback['ques18_tech1_cmnt'] or ' ',
                        'ques19_tech1': tech1_feedback['ques19_tech1'] or ' ',
                        'ques19_tech1_cmnt': tech1_feedback['ques19_tech1_cmnt'] or ' ',
                        'ques20_tech1': tech1_feedback['ques20_tech1'] or ' ',
                        'ques20_tech1_cmnt': tech1_feedback['ques20_tech1_cmnt'] or ' ',
                        'ques21_tech1': tech1_feedback['ques21_tech1'] or ' ',
                        'ques21_tech1_cmnt': tech1_feedback['ques21_tech1_cmnt'] or ' ',

                        'tech1_overall_cmnt': tech1_feedback['tech1_overall_cmnt'] or ' ',

                        'kanban_state':tech1_feedback['kanban_state'] or ' ',
                        'reason' : reason or ' ',

                       
                     }
        if tech1_feedback:
            html_data = """
                    <table class="table-sm">
                        <tr>
                            <th style="border:1px solid black;background-color:green;color:white;">Suitable For Role</th>
                            <th style="border:1px solid black;background-color:green;color:white;">Understanding Knowledge</th>
                            <th style="border:1px solid black;background-color:green;color:white;">Remarks</th>
                        </tr>
                        <tr>
                            <td style="border:1px solid black;">Pega Basics</td><td style="border:1px solid black;text-transform:uppercase;">%(ques1_tech1)s</td><td style="border:1px solid black;">%(ques1_tech1_cmnt)s</td>
                        </tr>
                        <tr>
                            <td style="border:1px solid black;">Pega 7 or 8</td><td style="border:1px solid black;text-transform:uppercase;">%(ques2_tech1)s</td><td style="border:1px solid black;">%(ques2_tech1_cmnt)s</td>
                        </tr>
                        <tr>
                            <td style="border:1px solid black;">Agents & Integration</td><td style="border:1px solid black;text-transform:uppercase;">%(ques3_tech1)s</td><td style="border:1px solid black;">%(ques3_tech1_cmnt)s</td>
                        </tr>
                        <tr>
                            <td style="border:1px solid black;">User Interface</td><td style="border:1px solid black;text-transform:uppercase;">%(ques4_tech1)s</td><td style="border:1px solid black;">%(ques4_tech1_cmnt)s</td>
                        </tr>
                        <tr>
                            <td style="border:1px solid black;">Security Model</td><td style="border:1px solid black;text-transform:uppercase;">%(ques5_tech1)s</td><td style="border:1px solid black;">%(ques5_tech1_cmnt)s</td>
                        </tr>
                        <tr>
                            <td style="border:1px solid black;">DB Concepts</td><td style="border:1px solid black;text-transform:uppercase;">%(ques6_tech1)s</td><td style="border:1px solid black;">%(ques6_tech1_cmnt)s</td>
                        </tr>
                        <tr>
                            <td style="border:1px solid black;">Reporting / ETL</td><td style="border:1px solid black;text-transform:uppercase;">%(ques7_tech1)s</td><td style="border:1px solid black;">%(ques7_tech1_cmnt)s</td>
                        </tr>
                        <tr>
                            <td style="border:1px solid black;">Debugging / Analysis</td><td style="border:1px solid black;text-transform:uppercase;">%(ques8_tech1)s</td><td style="border:1px solid black;">%(ques8_tech1_cmnt)s</td>
                        </tr>
                        <tr>
                            <td style="border:1px solid black;">Pega / Ext Frameworks</td><td style="border:1px solid black;text-transform:uppercase;">%(ques9_tech1)s</td><td style="border:1px solid black;">%(ques9_tech1_cmnt)s</td>
                        </tr>
                        <tr>
                            <td style="border:1px solid black;">Problem Solving Skills (Pega specific) </td><td style="border:1px solid black;text-transform:uppercase;">%(ques10_tech1)s</td><td style="border:1px solid black;">%(ques10_tech1_cmnt)s</td>
                        </tr>
                        <tr>
                            <td style="border:1px solid black;">Experience in Database & App/Web Server Tools</td><td style="border:1px solid black;text-transform:uppercase;">%(ques11_tech1)s</td><td style="border:1px solid black;">%(ques11_tech1_cmnt)s</td>
                        </tr>
                        <tr>
                            <td style="border:1px solid black;">Contributions to Pega Community / Pega Exchange </td><td style="border:1px solid black;text-transform:uppercase;">%(ques12_tech1)s</td><td style="border:1px solid black;">%(ques12_tech1_cmnt)s</td>
                        </tr>
                        <tr>
                            <td style="border:1px solid black;">Knowledge on Advanced Concepts like AI, Robotics,NLP</td><td style="border:1px solid black;text-transform:uppercase;">%(ques13_tech1)s</td><td style="border:1px solid black;">%(ques13_tech1_cmnt)s</td>
                        </tr>
                        <tr>
                            <td style="border:1px solid black;">Client Interfacing </td><td style="border:1px solid black;text-transform:uppercase;">%(ques14_tech1)s</td><td style="border:1px solid black;">%(ques14_tech1_cmnt)s</td>
                        </tr>
                        <tr>
                            <td style="border:1px solid black;">Pega Upgrade Experience</td><td style="border:1px solid black;text-transform:uppercase;">%(ques15_tech1)s</td><td style="border:1px solid black;">%(ques15_tech1_cmnt)s</td>
                        </tr>
                        <tr>
                            <td style="border:1px solid black;">Knowledge about DevOps concepts </td><td style="border:1px solid black;text-transform:uppercase;">%(ques16_tech1)s</td><td style="border:1px solid black;">%(ques16_tech1_cmnt)s</td>
                        </tr>
                        <tr>
                            <td style="border:1px solid black;">Ability to analyse problems & self-learn (IC)</td><td style="border:1px solid black;text-transform:uppercase;">%(ques17_tech1)s</td><td style="border:1px solid black;">%(ques17_tech1_cmnt)s</td>
                        </tr>
                        <tr>
                            <td style="border:1px solid black;">Understanding of IT Landscape & Infrastructure</td><td style="border:1px solid black;text-transform:uppercase;">%(ques18_tech1)s</td><td style="border:1px solid black;">%(ques18_tech1_cmnt)s</td>
                        </tr>
                        <tr>
                            <td style="border:1px solid black;">Leadership Skills </td><td style="border:1px solid black;text-transform:uppercase;">%(ques19_tech1)s</td><td style="border:1px solid black;">%(ques19_tech1_cmnt)s</td>
                        </tr>
                        <tr>
                            <td style="border:1px solid black;">Soft Skills/Communication</td><td style="border:1px solid black;text-transform:uppercase;">%(ques20_tech1)s</td><td style="border:1px solid black;">%(ques20_tech1_cmnt)s</td>
                        </tr>
                        <tr>
                            <td style="border:1px solid black;">Attitude </td><td style="border:1px solid black;text-transform:uppercase;">%(ques21_tech1)s</td><td style="border:1px solid black;">%(ques21_tech1_cmnt)s</td>
                        </tr>
                    </table>
                    <div style="padding-top:20px">
                        <h4> Over All Feedback </h4>
                        <p> %(tech1_overall_cmnt)s</p>
                    </div>
                    <div style="padding-top:20px">
                        <h4> Interview Result </h4>
                        <p><strong> %(kanban_state)s</strong></p>
                        <p> %(reason)s</p>
                    </div>

                     """%(tech1_data)



        if kw.get('applicant_id'):
            applicant= request.env['hr.applicant'].sudo().search([('id','=',int(kw.get('applicant_id')))])
            if tech1_feedback:
                mail_template = request.env.ref('instellars_interview_schedule.hr_notification_on_tech_evaluation')
                template_ctx = {'kanban_state':ks,'reason':reason}
                next_seq= applicant.stage_id.sequence + 1
                next_stage = request.env['hr.recruitment.stage'].sudo().search([('sequence','=',next_seq)])
                if applicant.stage_id.tech1_interview_feedback_enable == True:
                    applicant.sudo().write({'tech1_interview':html_data,'kanban_state':'progress','stage_id':next_stage.id})
                    mail_template.with_context(**template_ctx).sudo().send_mail(applicant.id, force_send=True)
                    return applicant
                elif applicant.stage_id.tech2_interview_feedback_enable == True:
                    applicant.sudo().write({'tech2_interview':html_data, 'kanban_state':'progress','stage_id':next_stage.id})
                    mail_template.with_context(**template_ctx).sudo().send_mail(applicant.id, force_send=True)
                    return applicant
                else:
                    return False

    

    @http.route(['/evaluation/form/submit/'], type='json', auth='public')
    def submit(self, aaplicant_id=None, advantages=None, **kw):

        tech1_result = self.update_evaluation_info(advantages, **kw)

        return {'stage_id': tech1_result.stage_id.id, 'applicant_id':kw.get('applicant_id') }

    def update_managerial_evaluation_info(self,  advantages, **kw):
        # Generate a new contract with the current modifications
        managerial_feedback = advantages['personal_info']
        if managerial_feedback['kanban_state'] == 'hold':
            reason = managerial_feedback['hold_reason']
            ks = 'Hold'
        elif managerial_feedback['kanban_state'] == 'blocked':
            reason = managerial_feedback['reject_reason']
            ks = 'Blocked'
        elif managerial_feedback['kanban_state'] == 're_schedule':
            reason = managerial_feedback['re_schedule_reason']
            ks = 'Re Scheduled'
        else:
            reason = ''
            ks = 'Selected For Next Round'

        managerial_data = {
                        'ques1': '',
                        'ques1_cmnt': managerial_feedback['ques1_cmnt'] or ' ',
                        'ques2':  ' ',
                        'ques2_cmnt': managerial_feedback['ques2_cmnt'] or ' ',
                        'ques3': ' ',
                        'ques3_cmnt': managerial_feedback['ques3_cmnt'] or ' ',
                        'ques4':' ',
                        'ques4_cmnt': managerial_feedback['ques4_cmnt'] or ' ',
                        'ques5': ' ',
                        'ques5_cmnt': managerial_feedback['ques5_cmnt'] or ' ',
                        'ques6':' ',
                        'ques6_cmnt': managerial_feedback['ques6_cmnt'] or ' ',
                        'ques7':' ',
                        'ques7_cmnt': managerial_feedback['ques7_cmnt'] or ' ',
                        'ques8':' ',
                        'ques8_cmnt': managerial_feedback['ques8_cmnt'] or ' ',
                        'ques9':' ',
                        'ques9_cmnt': managerial_feedback['ques9_cmnt'] or ' ',
                        'ques10': ' ',
                        'ques10_cmnt': managerial_feedback['ques10_cmnt'] or ' ',
                        'ques11': '',
                        # 'ques11_cmnt': managerial_feedback['ques11_cmnt'] or ' ',
                     

                        'managerial_overall_cmnt': managerial_feedback['managerial_overall_cmnt'] or ' ',

                        'kanban_state':managerial_feedback['kanban_state'] or ' ',
                        'reason' : reason or ' ',

                       
                     }

        if managerial_feedback:
            for each in range(10):
                managerial_data['ques'+str(each+1)] = ''
                managerial_data['ques'+str(each+1)] += '<td style="border:1px solid black;text-align:center;"><i class="fa fa-check-square-o "></i></td>' if int(managerial_feedback['ques'+str(each+1)]) == 5  else '<td style="border:1px solid black;text-align:center;"><i class="fa fa-square-o"></i></td>'
                managerial_data['ques'+str(each+1)] += '<td style="border:1px solid black;text-align:center;"><i class="fa fa-check-square-o "></i></td>' if int(managerial_feedback['ques'+str(each+1)]) == 4  else '<td style="border:1px solid black;text-align:center;"><i class="fa fa-square-o"></i></td>'
                managerial_data['ques'+str(each+1)] += '<td style="border:1px solid black;text-align:center;"><i class="fa fa-check-square-o "></i></td>' if int(managerial_feedback['ques'+str(each+1)]) == 3  else '<td style="border:1px solid black;text-align:center;"><i class="fa fa-square-o"></i></td>'
                managerial_data['ques'+str(each+1)] += '<td style="border:1px solid black;text-align:center;"><i class="fa fa-check-square-o "></i></td>' if int(managerial_feedback['ques'+str(each+1)]) == 2  else '<td style="border:1px solid black;text-align:center;"><i class="fa fa-square-o"></i></td>'
                managerial_data['ques'+str(each+1)] += '<td style="border:1px solid black;text-align:center;"><i class="fa fa-check-square-o "></i></td>' if int(managerial_feedback['ques'+str(each+1)]) == 1  else '<td style="border:1px solid black;text-align:center;"><i class="fa fa-square-o"></i></td>'

                # print(type(managerial_feedback['ques'+str(each+1)]),'^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
            managerial_data['ques11'] += '<td style="border:1px solid black;text-align:center;" rowspan="3"><i class="fa fa-check-square-o "></i></td>' if managerial_feedback['ques11'] == 'advance' else '<td style="border:1px solid black;text-align:center;" rowspan="3"><i class="fa fa-square-o"></i></td>'
            managerial_data['ques11'] += '<td style="border:1px solid black;text-align:center;" colspan="2" rowspan="3"><i class="fa fa-check-square-o "></i></td>' if managerial_feedback['ques11'] == 'advance_with_reserve' else '<td style="border:1px solid black;text-align:center;" colspan="2" rowspan="3"><i class="fa fa-square-o"></i></td>'
            managerial_data['ques11'] += '<td style="border:1px solid black;text-align:center;" colspan="2" rowspan="3"><i class="fa fa-check-square-o "></i></td>' if managerial_feedback['ques11'] == 'do_not_advance' else '<td style="border:1px solid black;text-align:center;" colspan="2" rowspan="3"><i class="fa fa-square-o"></i></td>'

                

            
            html_data = """
                    <div class="container">
                    <table class="table-sm">
                        <tr>
                            <td style="border:1px solid black;" colspan="6">Interview evaluation forms are to be completed by the interviewer to rank the candidate’s overall qualifications for the position for
                    which they have applied. Under each heading, the interviewer should give the candidate a numerical rating and write specific jobrelated comments in the space provided. The numerical rating system is based on the scale below</td>
                        </tr>
                        <tr>
                            <td style="border:1px solid black;"><strong>Scale:</strong></td>
                            <td style="border:1px solid black;">5 – Exceptional</td>
                            <td style="border:1px solid black;">4 – Above Average </td>
                            <td style="border:1px solid black;">3 – Average</td>
                            <td style="border:1px solid black;">2 – Satisfactory</td>
                            <td style="border:1px solid black;">1 – Unsatisfactory</td>

                        </tr>
                    </table>
                    <table class="table-sm">
                        <tr>
                            <th style="border:1px solid black;" rowspan="2" width="50%%"></th>
                            <th style="border:1px solid black;text-align:center" colspan="5">Rating</th>
                        </tr>
                        <tr>
                           
                            <th style="border:1px solid black;text-align:center;">5</th>
                            <th style="border:1px solid black;text-align:center;">4</th>
                            <th style="border:1px solid black;text-align:center;">3</th>
                            <th style="border:1px solid black;text-align:center;">2</th>
                            <th style="border:1px solid black;text-align:center;">1</th>
                        </tr>
                        <tr>
                            <td style="border:1px solid black;"><strong>Educational Background</strong> – Does the candidate have the appropriate educational qualifications or
                training for this position?<br/><strong>Comments:</strong>%(ques1_cmnt)s </td>
                            %(ques1)s
                                                      
                        </tr>
                        <tr>
                            <td style="border:1px solid black;"><strong>Prior Work Experience </strong> – Has the candidate acquired similar skills or qualifications through past work
                experiences?<br/><strong>Comments:</strong>%(ques2_cmnt)s </td>
                %(ques2)s
                            </tr>
                        <tr>
                            <td style="border:1px solid black;"><strong>Technical Qualifications/Experience </strong> – Does the candidate have the technical skills necessary for this
                position?<br/><strong>Comments:</strong>%(ques3_cmnt)s </td>
                            %(ques3)s
                            </tr>
                        <tr>
                            <td style="border:1px solid black;"><strong>Communication</strong> – How were the candidate’s communication skills during the interview?<br/><strong>Comments:</strong>%(ques4_cmnt)s </td>
                              %(ques4)s
                              </tr>
                        <tr>
                            <td style="border:1px solid black;"><strong>Candidate Interest</strong> – How much interest did the candidate show in the position and the organization?<br/><strong>Comments:</strong>%(ques5_cmnt)s </td>
                              %(ques5)s
                              </tr>
                        <tr>
                            <td style="border:1px solid black;"><strong>Knowledge of Organization </strong> –  Did the candidate research the organization prior to the interview?<br/><strong>Comments:</strong>%(ques6_cmnt)s </td>
                              %(ques6)s
                              </tr>
                        <tr>
                            <td style="border:1px solid black;"><strong>Teambuilding/Interpersonal Skills </strong> – Did the candidate demonstrate, through their answers, good
                teambuilding/interpersonal skills?<br/><strong>Comments:</strong>%(ques7_cmnt)s </td>
                              %(ques7)s
                              </tr>
                        <tr>
                            <td style="border:1px solid black;"><strong>Initiative</strong> – Did the candidate demonstrate, through their answers, a high degree of initiative?<br/><strong>Comments:</strong>%(ques8_cmnt)s </td>
                            %(ques8)s
                        </tr>
                        <tr>
                            <td style="border:1px solid black;"><strong>Time Management</strong> – Did the candidate demonstrate, through their answers, good time management skills?<br/><strong>Comments:</strong>%(ques9_cmnt)s </td>
                            %(ques9)s
                        </tr>
                        <tr>
                            <td style="border:1px solid black;"><strong>Customer Service/Client service </strong> – Did the candidate demonstrate, through their answers, a high level of customer/Client service skills/abilities?<br/><strong>Comments:</strong>%(ques10_cmnt)s </td>
                        %(ques10)s
                        </tr>
                        <tr>
                            <td style="border:1px solid black;" rowspan="4"><strong>Overall Impression and Recommendation </strong> – Summary of your perceptions of the candidate’s strengths/weaknesses. Final comments and recommendations for proceeding with the candidate.<br/><strong>Comments:</strong>%(managerial_overall_cmnt)s </td>
                            <th style="border:1px solid black;">Advance</th>
                            <th style="border:1px solid black;" colspan="2">Advance with reservations</th>
                            <th style="border:1px solid black;" colspan="2">Do notadvance</th>
                        </tr>
                        <tr>
                           %(ques11)s
                        </tr>
                    </table>
                    <div style="padding-top:20px">
                        <h4> Interview Result </h4>
                        <p><strong> %(kanban_state)s</strong></p>
                        <p> %(reason)s</p>
                    </div>
                </div>
                """%(managerial_data)



        if kw.get('applicant_id'):
            applicant= request.env['hr.applicant'].sudo().search([('id','=',int(kw.get('applicant_id')))])
            if managerial_feedback:
                if applicant.stage_id.managerial_interview_feedback_enable == True:
                    applicant.sudo().write({'managerial_interview':html_data,'kanban_state':managerial_feedback['kanban_state']})
                    return applicant
                else:
                    return False

    @http.route(['/managerial/evaluation/form/submit/'], type='json', auth='public')
    def managerial_round_submit(self, aaplicant_id=None, advantages=None, **kw):
        managerial_result = self.update_managerial_evaluation_info(advantages, **kw)

        return {'stage_id': managerial_result.stage_id.id, 'applicant_id':kw.get('applicant_id') }