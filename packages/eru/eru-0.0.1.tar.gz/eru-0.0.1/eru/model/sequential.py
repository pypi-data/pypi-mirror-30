from __future__ import absolute_import
from ..train import *
from ..utils import *
from ..metrics import *

class Model(object):
    def __init__(self):
        self.model = nn.Sequential()
        self.layer_num = 0
        self.complied = False
        self.data_loader = None
        self.data_generator = None
        self.training_length = None
        self.optimizer = None
        self.loss_func = None
        self.clip_norm = None
        self.progress_bar = None
        self.metrics = None
        self.output_categorical = True

    def add(self, layer):
        layer = layer.cuda()
        self.model.add_module("layer_{}".format(self.layer_num), layer)
        self.layer_num += 1

    def compile(self, optimizer="adam", criterion="crossentropy", clip_norm=True, metrics=[]):

        optimizer = get_optimizer(optimizer, self.model.parameters())
        self.criterion_string = criterion
        if isinstance(criterion, str):
            loss_func, self.output_categorical = get_loss_func(criterion)
        else:
            loss_func, self.output_categorical = criterion

        self.complied = True
        self.optimizer = optimizer
        self.loss_func = loss_func
        self.clip_norm = clip_norm
        self.metrics = metrics

    def train_one_epoch(self):
        if not self.complied:
            raise TypeError("Model need to be compiled before training")

        self.model.train()
        for batch, i in enumerate(range(0, self.training_length)):
            data, targets = next(self.data_generator)
            self.model.zero_grad()
            self.optimizer.zero_grad()
            output = self.model(data)
            loss = self.loss_func(output, targets)
            loss.backward()

            if self.clip_norm:
                torch.nn.utils.clip_grad_norm(self.model.parameters(), 0.25)

            self.optimizer.step()
            report = []

            if i % 10 == 0:
                if "loss" in self.metrics:
                    report.append(("loss", loss.data[0]))
                if "acc" in self.metrics:
                    accuracy = get_accuracy(self.criterion_string, output, targets, self.batch_size)
                    report.append(("acc", accuracy))
                if "perplexity" in self.metrics:
                    report.append(("perplexity", torch.exp(loss).data[0]))

                self.progress_bar.update(i, report)

    def repackage_hiddens(self):
        for layer in self.model:
            if layer.hidden is not None:
                layer.hidden = repackage_hidden(layer.hidden)

    def fit_generator(self, data_loader, batch_size, epochs, train_length=None):
        self.init_model(batch_size)

        if train_length is None:
            self.training_length = len(data_loader)
        else:
            self.training_length = train_length

        self.data_loader = data_loader
        self.data_generator = data_loader.generate()
        self.train_run(epochs=epochs)

    def train_run(self, epochs=1):
        try:
            for epoch in range(1, epochs + 1):
                self.progress_bar = Progbar(self.training_length)
                epoch_start_time = time.time()
                self.train_one_epoch()
                delta_time = time.time() - epoch_start_time
                print("\n")

        except KeyboardInterrupt:
            print("\n")
            print('-' * 89)
            print('Exiting from training early')

    def evaluation(self, test_loader, batch_size=1):
        self.init_model(batch_size)
        self.model.eval()

        text_generator = test_loader.generate()
        test_length = len(test_loader)
        test_progress_bar = Progbar(test_length)
        total_loss = 0
        total_acc = 0
        total_preplexity = 0

        for i in range(0, test_length):
            data, targets = next(text_generator)
            output = self.model(data)
            loss = self.loss_func(output, targets)
            total_loss += loss.data[0]
            report = []
            if "loss" in self.metrics:
                report.append(("loss", loss.data[0]))
                total_loss += loss.data[0]
            if "acc" in self.metrics:
                accuracy = get_accuracy(self.criterion_string, output, targets, self.batch_size)
                report.append(("acc", accuracy))
                total_acc += accuracy
            if "perplexity" in self.metrics:
                report.append(("perplexity", torch.exp(loss).data[0]))
                total_preplexity += total_preplexity.data[0]

            test_progress_bar.update(i, report)

        return total_loss / test_length, total_acc / test_length, total_preplexity / test_length

    def init_model(self, batch_size):
        self.batch_size = batch_size
        for layer in self.model:
            layer.batch_size = batch_size
            if layer.require_hidden:
                layer.init_hidden()

    def eval(self):
        self.init_model(1)

    def save(self, file_name):
        with open(file_name, 'wb') as f:
            torch.save(self.model, f)


class ModelGenerate(object):
    def __init__(self, model, dictionary):
        model.eval()
        self.model = model.model
        self.model.eval()
        self.dictionary = dictionary

    def generate(self, tempeture=1, num_word=1000):
        ntokens = len(self.dictionary)
        output_words = []
        input = Variable(torch.rand(1, 1).mul(ntokens).long(), volatile=True).cuda()
        for i in range(num_word):
            output = self.model(input)
            word_weights = output.squeeze().data.div(tempeture).exp().cpu()
            word_idx = torch.multinomial(word_weights, 1)[0]
            input.data.fill_(word_idx)
            word = self.dictionary.idx2word[word_idx]
            print(word, end=" ")
            output_words.append(word)

        return " ".join(output_words)


def load_model(file_name):
    with open(file_name, 'rb') as f:
        core_model = torch.load(f)

    model = Model()
    model.model = core_model
    return model


def epochs_report(epoch, delta_time, loss):
    print('-' * 89)
    print('| end of epoch {:3d} | time: {:5.2f}s | valid loss {:5.2f} |'.format(epoch, delta_time, loss))
    print('-' * 89)
