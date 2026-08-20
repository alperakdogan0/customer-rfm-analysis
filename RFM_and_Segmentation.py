import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)
pd.reset_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.3f' % x)

DATA_PATH = "data/online_retail_II.xlsx"
df = pd.read_excel(DATA_PATH, sheet_name="Year 2009-2010")

df = df_.copy()
df.head()
df.shape
df.isnull().sum()

###### 2 VERİYİ ANLAMA ######

df["Description"].nunique()
df["Description"].value_counts().head()

df.groupby("Description").agg({"Quantity": "sum"}).head()
df.groupby("Description").agg({"Quantity": "sum"}).sort_values("Quantity", ascending=False).head()

df["Invoice"].nunique()

df["TotalPrice"] = df["Quantity"] * df["Price"]

df.groupby("Invoice").agg({"TotalPrice": "sum"})

##### 3 VERİ HAZIRLAMA (DATA PREPARATION) ######

df.dropna(inplace=True)
df.shape
df.describe().T

df = df[~df["Invoice"].str.contains("C", na=False)]

###### 4 RFM METRİKLERİNİN HESAPLANMASI ######

df["InvoiceDate"].max()

today_date = dt.datetime(2010, 12, 11)
type(today_date)
df.head()
rfm = df.groupby("Customer ID").agg({"InvoiceDate": lambda InvoiceDate : (today_date - InvoiceDate.max()).days,
                                     "Invoice": lambda Invoice : Invoice.nunique(),
                                     "TotalPrice": lambda TotalPrice : TotalPrice.sum()})

rfm.head()
rfm.columns = ["recency", "frequency", "monetary"]

rfm.describe().T

rfm = rfm[rfm["monetary"] > 0 ]
rfm.shape


###### 5 RFM SKORLARININ HESAPLANMASI ######

rfm["recency_score"] = pd.qcut(rfm["recency"], 5, labels= [5, 4, 3, 2, 1])

rfm["monetary_score"] = pd.qcut(rfm["monetary"], 5, labels=[1, 2, 3, 4, 5])

rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])

rfm["RFM_SCORE"] = (rfm["recency_score"].astype(str) +
                    rfm["frequency_score"].astype(str))

rfm.head()

rfm[rfm["RFM_SCORE"] == "55"]
rfm[rfm["RFM_SCORE"] == "11"]


###### 6 RFM SEGMENTLERİNİN OLUŞTURULMASI ######

seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5' : 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customer',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm["segment"] = rfm["RFM_SCORE"].replace(seg_map, regex=True)

rfm.head()

rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])

rfm[rfm["segment"] == "at_Risk"].head()

rfm[rfm["segment"] == "new_customer"].index

new_df = pd.DataFrame()

new_df["new_customer_id"] = rfm[rfm["segment"] == "new_customer"].index
new_df["new_customer_id"] = new_df["new_customer_id"].astype(int)

new_df.to_csv("new_customers.csv")


###### 7 TUM SURECIN FONKSIYONLASTIRILMASI ######

def create_rfm(DataFrame, csv=False):
    # VERIYI HAZIRLAMA
    DataFrame["TotalPrice"] = DataFrame["Quantity"] * DataFrame["Price"]
    DataFrame.dropna(inplace=True)
    DataFrame = DataFrame[~DataFrame["Invoice"].str.contains("C", na=False)]

    # RFM METRIKLERININ HESAPLANMASI
    today_date = dt.datetime(2010, 12, 11)
    rfm = DataFrame.groupby("Customer ID").agg({"InvoiceDate": lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                                                "Invoice": lambda Invoice: Invoice.nunique(),
                                                "TotalPrice": lambda TotalPrice: TotalPrice.sum()})
    rfm.columns = ["recency", "frequency", "monetary"]

    # RFM SKORLARININ HESAPLANMASI
    rfm["recency_score"] = pd.qcut(rfm["recency"], 5, labels=[5, 4, 3, 2, 1])
    rfm["monetary_score"] = pd.qcut(rfm["monetary"], 5, labels=[1, 2, 3, 4, 5])
    rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])

    # SKORLARI KATEGORIK DEGISKENE CEVIRIP DF'E EKLEME
    rfm["RFM_SCORE"] = (rfm["recency_score"].astype(str) +
                        rfm["frequency_score"].astype(str))

    # SEGMENTLERIN ISIMLENDIRILMESI
    seg_map = {
        r'[1-2][1-2]': 'hibernating',
        r'[1-2][3-4]': 'at_Risk',
        r'[1-2]5': 'cant_loose',
        r'3[1-2]': 'about_to_sleep',
        r'33': 'need_attention',
        r'[3-4][4-5]': 'loyal_customers',
        r'41': 'promising',
        r'51': 'new_customer',
        r'[4-5][2-3]': 'potential_loyalists',
        r'5[4-5]': 'champions'
    }
    rfm["segment"] = rfm["RFM_SCORE"].replace(seg_map, regex=True)
    rfm = rfm[["recency", "frequency", "monetary", "segment"]]
    rfm.index = rfm.index.astype(int)

    if csv:
        rfm.to_csv("rfm_csv")
    return rfm


df = df_.copy()

rfm_new = create_rfm(df, csv=True)
