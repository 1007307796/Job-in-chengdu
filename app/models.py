from app import db

class Jobs(db.Model):
    __tablename__ = 'laGou'
    id = db.Column(db.Integer,primary_key=True)
    work_addr = db.Column(db.String(128))
    job_name = db.Column(db.String(128))
    detail_url = db.Column(db.String(64))
    data_from = db.Column(db.String(64))
    company_name = db.Column(db.String(64))

    def __repr__(self):
        return '<公司名:{}>'.format(self.company_name)